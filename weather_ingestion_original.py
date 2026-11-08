import json
from datetime import datetime
from pathlib import Path

import requests
import psycopg
import os


BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(location: str):
    """Get latitude and longitude for a location as part of a dictionary."""

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json() #returns a python dictionary
    
    print("****** in get_coordinates")
    print(data)

    if not data.get("results"):
        raise ValueError(f"Location not found: {location}")

    result = data["results"][0]
    

    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country"),
        "admin1": result.get("admin1")
    }


def get_weather(latitude: float, longitude: float):
    """Retrieve weather forecast from Open-Meteo."""

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],

        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max"
        ],

        "timezone": "auto",

        "forecast_days": 7
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()
    
    #print("*********** in get_weather, printing response")
    #print(response.json())
    

    return response.json()


def save_raw_data(data, location):
    """Save raw API response as JSON."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("************ in save_raw_data")
    print(timestamp)

    filename = (
        f"{location['name']}_"
        f"{timestamp}.json"
    )

    output_path = Path("data/raw") / filename

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Raw weather data saved to: {output_path}")


def main():
    
    '''
    conn = psycopg.connect(
    host="postgres:17",
    port=5432,
    dbname="weatherdb",
    user="datauser",
    password="LocalDev_Password_123!"
    )
    '''
    
    conn = psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="myapp",
    user="myapp_user",
    password="dev-password",
)

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version(), current_database();")
            print(cur.fetchone())
    finally:
        conn.close()
    
 
    location_name = "Milton"

    print(f"Searching for location: {location_name}")

    location = get_coordinates(location_name)

    print(
        f"Location found: "
        f"{location['name']}, "
        f"{location['admin1']}, "
        f"{location['country']}"
    )

    print(
        f"Coordinates: "
        f"{location['latitude']}, "
        f"{location['longitude']}"
    )

    weather_data = get_weather(
        location["latitude"],
        location["longitude"]
    )

    print("Weather data successfully retrieved.")

    
    save_raw_data(
        {
            "location": location,
            "weather": weather_data
        },
        location
    )
    


if __name__ == "__main__":
    main()