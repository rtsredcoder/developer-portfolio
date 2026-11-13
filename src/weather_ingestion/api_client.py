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
        print(endpoint)             # https://api.open-meteo.com/v1/forecasts  OR https://geocoding-api.open-meteo.com/v1/search
        
        print("params")
        print(params)
        # print(params['name'])           #e.g. {'name': 'Toronto', 'count': 1, 'language': 'en', 'format': 'json'}

        
        
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

                if (endpoint == FORECAST_URL):
                    pass

                    # {sample response value when calling GEOCODING_URL  [{'id': 6167865, 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'elevation': 161.0, 'feature_code': 'PPLA', 'country_code': 'CA', 'admin1_id': 6093943, 'timezone': 'America/Toronto', 'population': 2794356, 'country_id': 6251999, 'country': 'Canada', 'admin1': 'Ontario'}], 'generationtime_ms': 0.13911724}
                    # sample response value when calling FORECAST_URL for hourly = {'latitude': 43.70455, 'longitude': -79.404625, 'generationtime_ms': 0.43380260467529297, 'utc_offset_seconds': -18000, 'timezone': 'America/Toronto', 'timezone_abbreviation': 'GMT-5', 'elevation': 165.0, 'hourly_units': {'time': 'iso8601', 'temperature_2m': '°C', 'relative_humidity_2m': '%', 'precipitation_probability': '%', 'precipitation': 'mm', 'weather_code': 'wmo code', 'wind_speed_10m': 'km/h'}, 'hourly': {'time': ['2026-11-12T00:00', '2026-11-12T01:00', '2026-11-12T02:00', '2026-11-12T03:00', '2026-11-12T04:00', '2026-11-12T05:00', '2026-11-12T06:00', '2026-11-12T07:00', '2026-11-12T08:00', '2026-11-12T09:00', '2026-11-12T10:00', '2026-11-12T11:00', '2026-11-12T12:00', '2026-11-12T13:00', '2026-11-12T14:00', '2026-11-12T15:00', '2026-11-12T16:00', '2026-11-12T17:00', '2026-11-12T18:00', '2026-11-12T19:00', '2026-11-12T20:00', '2026-11-12T21:00', '2026-11-12T22:00', '2026-11-12T23:00', '2026-11-13T00:00', '2026-11-13T01:00', '2026-11-13T02:00', '2026-11-13T03:00', '2026-11-13T04:00', '2026-11-13T05:00', '2026-11-13T06:00', '2026-11-13T07:00', '2026-11-13T08:00', '2026-11-13T09:00', '2026-11-13T10:00', '2026-11-13T11:00', '2026-11-13T12:00', '2026-11-13T13:00', '2026-11-13T14:00', '2026-11-13T15:00', '2026-11-13T16:00', '2026-11-13T17:00', '2026-11-13T18:00', '2026-11-13T19:00', '2026-11-13T20:00', '2026-11-13T21:00', '2026-11-13T22:00', '2026-11-13T23:00', '2026-11-14T00:00', '2026-11-14T01:00', '2026-11-14T02:00', '2026-11-14T03:00', '2026-11-14T04:00', '2026-11-14T05:00', '2026-11-14T06:00', '2026-11-14T07:00', '2026-11-14T08:00', '2026-11-14T09:00', '2026-11-14T10:00', '2026-11-14T11:00', '2026-11-14T12:00', '2026-11-14T13:00', '2026-11-14T14:00', '2026-11-14T15:00', '2026-11-14T16:00', '2026-11-14T17:00', '2026-11-14T18:00', '2026-11-14T19:00', '2026-11-14T20:00', '2026-11-14T21:00', '2026-11-14T22:00', '2026-11-14T23:00', '2026-11-15T00:00', '2026-11-15T01:00', '2026-11-15T02:00', '2026-11-15T03:00', '2026-11-15T04:00', '2026-11-15T05:00', '2026-11-15T06:00', '2026-11-15T07:00', '2026-11-15T08:00', '2026-11-15T09:00', '2026-11-15T10:00', '2026-11-15T11:00', '2026-11-15T12:00', '2026-11-15T13:00', '2026-11-15T14:00', '2026-11-15T15:00', '2026-11-15T16:00', '2026-11-15T17:00', '2026-11-15T18:00', '2026-11-15T19:00', '2026-11-15T20:00', '2026-11-15T21:00', '2026-11-15T22:00', '2026-11-15T23:00', '2026-11-16T00:00', '2026-11-16T01:00', '2026-11-16T02:00', '2026-11-16T03:00', '2026-11-16T04:00', '2026-11-16T05:00', '2026-11-16T06:00', '2026-11-16T07:00', '2026-11-16T08:00', '2026-11-16T09:00', '2026-11-16T10:00', '2026-11-16T11:00', '2026-11-16T12:00', '2026-11-16T13:00', '2026-11-16T14:00', '2026-11-16T15:00', '2026-11-16T16:00', '2026-11-16T17:00', '2026-11-16T18:00', '2026-11-16T19:00', '2026-11-16T20:00', '2026-11-16T21:00', '2026-11-16T22:00', '2026-11-16T23:00', '2026-11-17T00:00', '2026-11-17T01:00', '2026-11-17T02:00', '2026-11-17T03:00', '2026-11-17T04:00', '2026-11-17T05:00', '2026-11-17T06:00', '2026-11-17T07:00', '2026-11-17T08:00', '2026-11-17T09:00', '2026-11-17T10:00', '2026-11-17T11:00', '2026-11-17T12:00', '2026-11-17T13:00', '2026-11-17T14:00', '2026-11-17T15:00', '2026-11-17T16:00', '2026-11-17T17:00', '2026-11-17T18:00', '2026-11-17T19:00', '2026-11-17T20:00', '2026-11-17T21:00', '2026-11-17T22:00', '2026-11-17T23:00', '2026-11-18T00:00', '2026-11-18T01:00', '2026-11-18T02:00', '2026-11-18T03:00', '2026-11-18T04:00', '2026-11-18T05:00', '2026-11-18T06:00', '2026-11-18T07:00', '2026-11-18T08:00', '2026-11-18T09:00', '2026-11-18T10:00', '2026-11-18T11:00', '2026-11-18T12:00', '2026-11-18T13:00', '2026-11-18T14:00', '2026-11-18T15:00', '2026-11-18T16:00', '2026-11-18T17:00', '2026-11-18T18:00', '2026-11-18T19:00', '2026-11-18T20:00', '2026-11-18T21:00', '2026-11-18T22:00', '2026-11-18T23:00'], 'temperature_2m': [7.1, 7.0, 6.3, 5.8, 5.4, 5.1, 4.8, 4.4, 3.8, 4.2, 5.0, 5.5, 6.4, 7.1, 7.5, 7.3, 6.5, 5.1, 4.1, 4.1, 2.9, 2.0, 1.9, 1.1, 0.5, 0.1, -0.0, -0.3, -0.5, -0.5, -0.5, -0.7, -0.1, 1.5, 1.6, 1.8, 3.0, 3.1, 3.1, 3.3, 3.2, 2.5, 1.7, 1.1, 1.5, 1.7, 1.2, 0.5, 0.6, 1.2, 1.2, 1.1, 1.5, 1.3, 2.1, 2.3, 2.6, 3.5, 4.4, 5.2, 5.5, 5.6, 5.7, 6.1, 5.5, 4.6, 4.2, 4.4, 4.7, 4.5, 4.3, 4.1, 4.0, 3.9, 4.1, 4.1, 3.9, 3.2, 2.7, 2.5, 3.4, 3.8, 3.9, 4.5, 5.6, 5.9, 5.9, 5.7, 5.9, 5.3, 4.6, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.2, 5.3, 5.3, 5.3, 5.5, 5.6, 5.5, 5.6, 5.8, 6.5, 7.4, 7.9, 8.1, 8.2, 8.2, 8.2, 8.0, 7.4, 6.7, 6.2, 5.7, 5.3, 5.0, 4.7, 4.4, 4.2, 4.0, 3.9, 3.7, 3.5, 3.4, 3.7, 4.9, 6.5, 8.2, 9.7, 10.8, 11.2, 11.2, 10.8, 10.0, 8.9, 8.0, 7.3, 6.8, 6.3, 5.9, 5.6, 5.4, 5.1, 4.9, 4.7, 4.4, 4.2, 4.3, 5.0, 6.1, 7.2, 8.5, 9.9, 10.8, 11.2, 11.2, 10.9, 10.2, 9.3, 8.5, 8.0, 7.5, 7.1, 6.9], 'relative_humidity_2m': [94, 89, 92, 91, 90, 91, 86, 86, 90, 86, 79, 74, 69, 62, 62, 61, 59, 62, 65, 66, 67, 70, 71, 73, 71, 75, 73, 76, 76, 74, 74, 80, 83, 84, 85, 84, 68, 58, 67, 63, 61, 65, 70, 73, 74, 77, 73, 74, 78, 79, 79, 85, 87, 87, 85, 84, 84, 84, 80, 74, 73, 71, 71, 70, 72, 79, 83, 86, 86, 79, 75, 71, 69, 68, 66, 65, 66, 69, 72, 71, 63, 63, 63, 60, 54, 51, 52, 59, 59, 62, 65, 62, 61, 61, 60, 60, 59, 59, 59, 59, 60, 60, 60, 61, 63, 65, 63, 56, 53, 53, 54, 54, 54, 55, 58, 61, 64, 66, 70, 72, 73, 73, 73, 73, 73, 73, 74, 75, 75, 70, 65, 57, 49, 43, 41, 42, 44, 48, 53, 57, 59, 61, 62, 62, 62, 62, 62, 62, 62, 63, 64, 64, 61, 57, 52, 47, 42, 39, 38, 39, 41, 46, 52, 58, 64, 70, 75, 77], 'precipitation_probability': [59, 52, 53, 40, 63, 36, 15, 12, 5, 14, 17, 12, 5, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 3, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 4, 3, 2, 2, 2, 3, 12, 9, 9, 9, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'precipitation': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'weather_code': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 0, 0, 1, 0, 0, 2, 3, 0, 3, 3, 2, 1, 0, 0, 1, 3, 3, 3, 2, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 2, 3, 2, 51, 3, 3, 3, 1, 3, 3, 3, 3, 3, 0, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 1, 2], 'wind_speed_10m': [8.0, 12.3, 12.8, 11.2, 17.2, 16.1, 15.6, 20.4, 19.4, 18.2, 18.4, 15.8, 17.9, 19.1, 16.7, 16.6, 17.6, 11.3, 13.0, 16.3, 18.1, 15.9, 14.6, 13.4, 12.3, 11.4, 12.6, 12.2, 10.9, 12.0, 11.9, 7.5, 9.8, 11.5, 12.0, 12.6, 13.7, 15.8, 14.3, 13.3, 13.4, 8.7, 6.4, 8.6, 10.3, 9.9, 10.0, 8.4, 8.6, 10.4, 9.9, 8.3, 9.3, 9.7, 12.6, 16.1, 17.4, 19.2, 20.4, 20.7, 21.8, 23.6, 24.1, 24.0, 22.9, 20.7, 17.2, 14.4, 13.9, 13.4, 13.8, 14.4, 14.5, 14.2, 14.5, 13.8, 13.5, 13.2, 13.3, 12.3, 12.7, 12.2, 12.9, 13.6, 13.8, 15.2, 15.3, 12.9, 12.2, 11.4, 10.3, 12.3, 11.6, 9.0, 9.4, 10.5, 8.8, 9.0, 8.9, 9.2, 8.4, 8.2, 6.6, 3.6, 4.5, 5.6, 6.3, 7.2, 9.8, 10.8, 11.0, 10.8, 10.2, 8.2, 5.9, 5.8, 6.2, 6.8, 6.8, 6.5, 6.5, 7.0, 6.7, 6.6, 7.7, 7.8, 7.5, 8.2, 8.0, 9.7, 11.1, 11.6, 12.3, 12.6, 11.9, 10.7, 9.7, 9.3, 9.3, 9.3, 8.9, 8.5, 8.1, 7.9, 7.3, 7.1, 7.1, 7.1, 7.1, 6.8, 6.9, 6.9, 7.6, 8.7, 9.5, 10.5, 11.1, 11.2, 10.3, 8.9, 7.7, 7.4, 7.1, 7.1, 7.4, 7.6, 7.9, 7.9]}}

                try:
                    # set payload to the the API response
                    payload = response.json()     
                except ValueError as exc:
                    raise OpenMeteoError(f"Invalid JSON returned by {endpoint}") from exc
                if not isinstance(payload, dict):
                    raise OpenMeteoError(f"Expected JSON object from {endpoint}")

                print("***************** in api_client.py --> _get_json() --> after calling endpoint")
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

        print("************ in api_client.py --> Class OpenMeteoClient --> method forecast()")
        print("data_kind")
        print(data_kind)

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

        print("**************** in forecast() method --> params variable before calling _get_json() method")
        print("params")
        print(params)  # e.g. {'latitude': 43.70643, 'longitude': -79.39864, 'hourly': ['temperature_2m', 'relative_humidity_2m', 'precipitation_probability', 'precipitation', 'weather_code', 'wind_speed_10m'], 'timezone': 'auto', 'forecast_days': 7}


        # call _get_json_ method to pull from endpoint, note that this is based on lat / longitude, and not on city name
        payload, status = self._get_json(FORECAST_URL, params)
        return payload, params, status
