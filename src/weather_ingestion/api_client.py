from __future__ import annotations

import random
import time
from typing import Any

import requests

import sys

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class OpenMeteoError(RuntimeError):
    """Raised when Open-Meteo requests fail or return invalid JSON."""


class OpenMeteoClient:

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        max_retries: int = 4,
        backoff_base_seconds: float = 0.75,
        session: requests.Session | None = None,
        sleep=time.sleep,
        random_uniform=random.uniform,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.session = session or requests.Session()
        self.sleep = sleep
        self.random_uniform = random_uniform

        print("********** api_client.py --> Class OpenMeteoClient --> __init method__")
        print("self.sleep")
        print("self.sleep")
        print(sleep)
        
        print("self.random_uniform")
        print(self.random_uniform)

    def _get_json(self, endpoint: str, params: dict[str, Any]) -> tuple[dict, int]:
        print("f***************** in api_client.py --> class OpenMeteoClient() --> method _get_json() against URL: {endpoint}")
        
        print("endpoint")
        print(endpoint)             # https://api.open-meteo.com/v1/forecasts
        
        print("params")
        print(params)
        print(params['name'])           #e.g. {'name': 'Toronto', 'count': 1, 'language': 'en', 'format': 'json'}

        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    endpoint, params=params, timeout=(self.timeout_seconds, self.timeout_seconds)
                )

               


                status = response.status_code
                if status in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                    self._backoff(attempt)
                    continue
                response.raise_for_status()

                print("response.json()")
                print(response.json())          # {'results': [{'id': 6167865, 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'elevation': 161.0, 'feature_code': 'PPLA', 'country_code': 'CA', 'admin1_id': 6093943, 'timezone': 'America/Toronto', 'population': 2794356, 'country_id': 6251999, 'country': 'Canada', 'admin1': 'Ontario'}], 'generationtime_ms': 0.13911724}



                try:
                    payload = response.json()     # {'results': [{'id': 6167865, 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'elevation': 161.0, 'feature_code': 'PPLA', 'country_code': 'CA', 'admin1_id': 6093943, 'timezone': 'America/Toronto', 'population': 2794356, 'country_id': 6251999, 'country': 'Canada', 'admin1': 'Ontario'}], 'generationtime_ms': 0.13911724}
                except ValueError as exc:
                    raise OpenMeteoError(f"Invalid JSON returned by {endpoint}") from exc
                if not isinstance(payload, dict):
                    raise OpenMeteoError(f"Expected JSON object from {endpoint}")

                print("***************** in api_client.py --> _get_json() --> after calling GEOCODING_URL")
                print("payload")
                print(payload)
                print("status")
                print(status)                
                return payload, status          #return payload and status and then return to calling function


            
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt >= self.max_retries:
                    raise OpenMeteoError(
                        f"Request failed after {attempt + 1} attempts: {endpoint}"
                    ) from exc
                self._backoff(attempt)
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "unknown"
                raise OpenMeteoError(f"HTTP error {status} from {endpoint}") from exc
            except requests.RequestException as exc:
                raise OpenMeteoError(f"Request error from {endpoint}: {exc}") from exc
        raise OpenMeteoError(f"Request failed: {endpoint}")  # defensive

    def _backoff(self, attempt: int) -> None:
        delay = self.backoff_base_seconds * (2**attempt)
        delay += self.random_uniform(0, min(0.25, delay * 0.25)) if delay else 0
        self.sleep(delay)

    def geocode(self, name: str) -> tuple[dict[str, Any], dict[str, Any], int]:
        # takes a city name as string parameter, and returns a tuple of (location (dictionary), params (dictionary), status code)
        print("****************** in api_client.py --> class OpenMeteoClient --> method geocode()**************")
        print(f"name: {name}")
        params = {"name": name, "count": 1, "language": "en", "format": "json"}
        payload, status = self._get_json(GEOCODING_URL, params)

        # payload = {'results': [{'id': 6167865, 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'elevation': 161.0, 'feature_code': 'PPLA', 'country_code': 'CA', 'admin1_id': 6093943, 'timezone': 'America/Toronto', 'population': 2794356, 'country_id': 6251999, 'country': 'Canada', 'admin1': 'Ontario'}], 'generationtime_ms': 0.13911724}

        print(f"payload: {payload}")   #information about the city passed in
        print(f"status: {status}")     # e.g. 200

        results = payload.get("results") or []

        print("results")
        print(results)    # [{'id': 6167865, 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'elevation': 161.0, 'feature_code': 'PPLA', 'country_code': 'CA', 'admin1_id': 6093943, 'timezone': 'America/Toronto', 'population': 2794356, 'country_id': 6251999, 'country': 'Canada', 'admin1': 'Ontario'}]

        if not results:
            raise OpenMeteoError(f"Location not found: {name}")
        result = results[0]
        location = {
            "location_id": self.location_id(result),
            "name": result["name"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result.get("country"),
            "admin1": result.get("admin1"),
            "timezone": result.get("timezone"),
        }

        print("location variable after being calculated in geocode method")
        print(type(location))       # <class 'dict'>
        print(location)    # {'location_id': 'toronto-43.70643--79.39864', 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'country': 'Canada', 'admin1': 'Ontario', 'timezone': 'America/Toronto'}

        print("params variable in geocode method")
        print(type(params))
        print(params)   # {'name': 'Toronto', 'count': 1, 'language': 'en', 'format': 'json'}.... this was set above manually

        print("****************** about to exit from OpenMeteoClient --> geocode method *******")
        return location, params, status

    @staticmethod
    def location_id(location: dict[str, Any]) -> str:
        # Stable identifier based on resolved place and coordinates, independent of run time.
        name = str(location.get("name", "location")).strip().lower()
        slug = "".join(ch if ch.isalnum() else "-" for ch in name).strip("-")
        return f"{slug}-{location.get('latitude')}-{location.get('longitude')}"

    def forecast(
        self, latitude: float, longitude: float, data_kind: str, forecast_days: int = 7
    ) -> tuple[dict[str, Any], dict[str, Any], int]:
        if data_kind == "hourly":
            fields = [
                "temperature_2m", "relative_humidity_2m", "precipitation_probability",
                "precipitation", "weather_code", "wind_speed_10m",
            ]
        elif data_kind == "daily":
            fields = [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum",
                "precipitation_probability_max", "wind_speed_10m_max",
            ]
        else:
            raise ValueError("data_kind must be 'hourly' or 'daily'")
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            data_kind: fields,
            "timezone": "auto",
            "forecast_days": forecast_days,
        }
        payload, status = self._get_json(FORECAST_URL, params)
        return payload, params, status
