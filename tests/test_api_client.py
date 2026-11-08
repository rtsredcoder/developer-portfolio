import requests
import pytest

from weather_ingestion.api_client import (
    OpenMeteoClient, OpenMeteoError, FORECAST_URL, GEOCODING_URL
)


class FakeResponse:
    def __init__(self, payload=None, status_code=200, json_error=None):
        self._payload = payload or {}
        self.status_code = status_code
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"HTTP {self.status_code}")
            error.response = self
            raise error


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append((url, params, timeout))
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_forecast_sends_hourly_params_and_timeout():
    session = FakeSession([FakeResponse({"hourly": {"time": []}})])
    client = OpenMeteoClient(session=session)
    payload, params, status = client.forecast(43.7, -79.4, "hourly", 3)
    assert payload["hourly"]["time"] == []
    assert params["forecast_days"] == 3
    assert "temperature_2m" in params["hourly"]
    assert status == 200
    assert session.calls[0][0] == FORECAST_URL
    assert session.calls[0][2] == (20.0, 20.0)


def test_geocode_returns_stable_location_id():
    session = FakeSession([FakeResponse({"results": [{
        "name": "Milton", "latitude": 43.5, "longitude": -79.9,
        "country": "Canada", "admin1": "Ontario"
    }]})])
    location, params, status = OpenMeteoClient(session=session).geocode("Milton")
    assert location["location_id"] == "milton-43.5--79.9"
    assert params["name"] == "Milton"
    assert status == 200
    assert session.calls[0][0] == GEOCODING_URL


def test_retries_timeout_then_succeeds():
    session = FakeSession([
        requests.Timeout("slow"),
        FakeResponse({"daily": {"time": []}})
    ])
    sleeps = []
    client = OpenMeteoClient(session=session, max_retries=1, sleep=sleeps.append,
                             random_uniform=lambda a, b: 0)
    payload, _, _ = client.forecast(43, -79, "daily")
    assert "daily" in payload
    assert len(session.calls) == 2
    assert sleeps == [0.75]


def test_retries_429_then_succeeds():
    session = FakeSession([FakeResponse(status_code=429), FakeResponse({"results": []})])
    sleeps = []
    client = OpenMeteoClient(session=session, max_retries=1, sleep=sleeps.append,
                             random_uniform=lambda a, b: 0)
    payload, _ = client._get_json(GEOCODING_URL, {"name": "X"})
    assert payload == {"results": []}
    assert len(session.calls) == 2
    assert sleeps == [0.75]


def test_non_retryable_http_error_fails_immediately():
    session = FakeSession([FakeResponse(status_code=400)])
    client = OpenMeteoClient(session=session, max_retries=3, sleep=lambda _: None)
    with pytest.raises(OpenMeteoError, match="HTTP error 400"):
        client._get_json(FORECAST_URL, {})
    assert len(session.calls) == 1


def test_retry_exhaustion_raises_clear_error():
    session = FakeSession([requests.ConnectionError("offline"), requests.ConnectionError("offline")])
    client = OpenMeteoClient(session=session, max_retries=1, sleep=lambda _: None,
                             random_uniform=lambda a, b: 0)
    with pytest.raises(OpenMeteoError, match="after 2 attempts"):
        client._get_json(FORECAST_URL, {})


def test_invalid_json_raises_domain_error():
    session = FakeSession([FakeResponse(json_error=ValueError("bad json"))])
    with pytest.raises(OpenMeteoError, match="Invalid JSON"):
        OpenMeteoClient(session=session)._get_json(FORECAST_URL, {})
