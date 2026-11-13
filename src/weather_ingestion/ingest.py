from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .api_client import OpenMeteoClient, FORECAST_URL, GEOCODING_URL
from .config import Settings

import sys

logger = logging.getLogger(__name__)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "location"


def _write_json_exclusive(path: Path, payload: Any) -> None:
    # create the path, e.g.  data/raw/run_id=20261113T032916174100Z-03830793/toronto
    path.parent.mkdir(parents=True, exist_ok=True)
    # x-mode refuses to overwrite even if a path collision occurs.
    with path.open("x", encoding="utf-8") as stream:

        print("********** in ingest.py --> _write_json_exclusive method")  #LEFT OFF HERE...
        print("payload")
        print(payload)
        # e.g. payload = {'requested_name': 'Toronto', 'resolved_location': {'location_id': 'toronto-43.70643--79.39864', 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'country': 'Canada', 'admin1': 'Ontario', 'timezone': 'America/Toronto'}}
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run_ingestion(
    settings: Settings,
    client: OpenMeteoClient | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    print("***************** got into run_ingestion method")
    client = client or OpenMeteoClient(
        timeout_seconds=settings.timeout_seconds,
        max_retries=settings.max_retries,
        backoff_base_seconds=settings.backoff_base_seconds,
    )

   

   
    clock = now or (lambda: datetime.now(timezone.utc))
    started = clock().astimezone(timezone.utc)
    run_id = started.strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = settings.raw_data_dir / f"run_id={run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)

    print("********* generating for run_id: ")
    print(run_id)
    print("********* run_dir ")
    print(run_dir)



    manifest: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "ingestion_started_at": started.isoformat(),
        "ingestion_completed_at": None,
        "source": "Open-Meteo",
        "records": [],
    }

    print("***************: manifest after being initialized in ingest.py run_ingestion() method")
    print(manifest)

    print("                    ")

    # for each location in settings.locations (Settings class / instance variable), pull data... this is the bulk of the program...
    # manifest object gets updated on each iteration...
    for requested_name in settings.locations:
        print("************* iterating through settings.locations for city: ")
        print(requested_name)
        location: dict[str, Any] | None = None
        try:
            #this returns (dict, dict, status code from OpenMetoClient class geocode() method), it will have the location name, lat., long., ID, etc
            location, geocode_params, geocode_status = client.geocode(requested_name)   
            
            location_dir = run_dir / _slug(location["name"])   # e.g. data/raw/run_id=20261110T115107818619Z-8e6ec7ee/toronto

            _write_json_exclusive(location_dir / "geocoding.json", {
                "requested_name": requested_name,
                "resolved_location": location,    #location = a dictinary from the client.geocode(requested_name) call just above, e.g.  {'location_id': 'toronto-43.70643--79.39864', 'name': 'Toronto', 'latitude': 43.70643, 'longitude': -79.39864, 'country': 'Canada', 'admin1': 'Ontario', 'timezone': 'America/Toronto'}
            })

            print("************* exiting after first _write_json_exclusive() method *************")
            # at this point it would have written a geocoding.json file, e.g. data/raw/run_id=20261113T032916174100Z-03830793/toronto/geocoding.json, and it would contain the location variable / dictionary from above
          
            manifest["records"].append({   #append() used to add items to the end of the 'records' list in manifest
                "ingestion_time": clock().astimezone(timezone.utc).isoformat(),
                "location_id": location["location_id"],
                "location_name": location["name"],
                "requested_name": requested_name,
                "source_endpoint": GEOCODING_URL,
                "request_parameters": geocode_params,
                "http_status": geocode_status,
                "artifact": str((location_dir / "geocoding.json").relative_to(run_dir)),
                "status": "success",
            })

            print("**************** manifest['records'] value before going into hourly / daily iterations ****************")
            print(manifest["records"])

            # manifest['records'] is a list which contains a dictionary = [{'ingestion_time': '2026-11-13T03:49:04.039982+00:00', 'location_id': 'toronto-43.70643--79.39864', 'location_name': 'Toronto', 'requested_name': 'Toronto', 'source_endpoint': 'https://geocoding-api.open-meteo.com/v1/search', 'request_parameters': {'name': 'Toronto', 'count': 1, 'language': 'en', 'format': 'json'}, 'http_status': 200, 'artifact': 'toronto/geocoding.json', 'status': 'success'}]
            # it also contains the openmeteo endpoint API

        except Exception as exc:
            logger.exception("geocoding_failed", extra={"event": "geocoding_failed", "location": requested_name})
            manifest["records"].append({
                "ingestion_time": clock().astimezone(timezone.utc).isoformat(),
                "location_id": None,
                "location_name": requested_name,
                "source_endpoint": GEOCODING_URL,
                "request_parameters": {"name": requested_name, "count": 1, "language": "en", "format": "json"},
                "artifact": None,
                "status": "failed",
                "error": str(exc),
            })
            continue

        # run through this for loop for both hourly and daily "data_kind" timeframes, pulling from https://geocoding-api.open-meteo.com/v1/search each time
        for data_kind in ("hourly", "daily"):
            try:
                payload, params, status = client.forecast(   #left off here, once it returns the tuple withthe hourly / daily data... see how it is writing it out...
                    location["latitude"], location["longitude"], data_kind, settings.forecast_days
                )


                artifact = location_dir / f"{data_kind}.json"
                _write_json_exclusive(artifact, payload)
                manifest["records"].append({
                    "ingestion_time": clock().astimezone(timezone.utc).isoformat(),
                    "location_id": location["location_id"],
                    "location_name": location["name"],
                    "source_endpoint": FORECAST_URL,
                    "request_parameters": params,
                    "http_status": status,
                    "artifact": str(artifact.relative_to(run_dir)),
                    "status": "success",
                })
                logger.info("ingestion_succeeded", extra={
                    "event": "ingestion_succeeded", "run_id": run_id,
                    "location_id": location["location_id"], "data_kind": data_kind,
                    "artifact": str(artifact),
                })
            except Exception as exc:
                logger.exception("forecast_ingestion_failed", extra={
                    "event": "forecast_ingestion_failed", "run_id": run_id,
                    "location": requested_name, "data_kind": data_kind,
                })
                manifest["records"].append({
                    "ingestion_time": clock().astimezone(timezone.utc).isoformat(),
                    "location_id": location["location_id"],
                    "location_name": location["name"],
                    "source_endpoint": FORECAST_URL,
                    "request_parameters": {
                        "latitude": location["latitude"], "longitude": location["longitude"],
                        "data_kind": data_kind, "forecast_days": settings.forecast_days,
                    },
                    "artifact": None,
                    "status": "failed",
                    "error": str(exc),
                })

    #  repeat for the next city in settings.location and also ends for loop to iterate each city, e.g. for requested_name in settings.locations:


    # close off the manifest file properties and then write it out using _write_json_exclusive()
    manifest["ingestion_completed_at"] = clock().astimezone(timezone.utc).isoformat()
    manifest_path = run_dir / "manifest.json"
    _write_json_exclusive(manifest_path, manifest)
    failed = sum(record["status"] == "failed" for record in manifest["records"])
    logger.info("ingestion_run_completed", extra={
        "event": "ingestion_run_completed", "run_id": run_id,
        "record_count": len(manifest["records"]), "failed_count": failed,
        "manifest": str(manifest_path),
    })
    return manifest
