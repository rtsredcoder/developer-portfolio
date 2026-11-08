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
    path.parent.mkdir(parents=True, exist_ok=True)
    # x-mode refuses to overwrite even if a path collision occurs.
    with path.open("x", encoding="utf-8") as stream:
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

    # for each location in settings.locations, pull data... this is the bulk of the program...
    # left off here...  manifest object gets updated on each iteration...
    for requested_name in settings.locations:
        print("************* iterating through settings.locations for city: ")
        print(requested_name)
        location: dict[str, Any] | None = None
        try:
            location, geocode_params, geocode_status = client.geocode(requested_name)
            location_dir = run_dir / _slug(location["name"])
            _write_json_exclusive(location_dir / "geocoding.json", {
                "requested_name": requested_name,
                "resolved_location": location,
            })
            manifest["records"].append({
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

        for data_kind in ("hourly", "daily"):
            try:
                payload, params, status = client.forecast(
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
