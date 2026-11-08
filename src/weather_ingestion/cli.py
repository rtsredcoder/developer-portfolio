from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import Settings
from .ingest import run_ingestion


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("event", "run_id", "location", "location_id", "data_kind",
                    "artifact", "manifest", "record_count", "failed_count"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level, logging.INFO))


def main() -> int:
    print("***************** in cli.py --> main() function")
    parser = argparse.ArgumentParser(description="Ingest raw hourly and daily Open-Meteo forecasts.")
    parser.add_argument("--locations", help="Comma-separated location names; overrides LOCATIONS.")
    parser.add_argument("--forecast-days", type=int, help="Forecast horizon (1-16); overrides FORECAST_DAYS.")
    args = parser.parse_args()
    print("************ args")
    print(args)
    # System.exit(0)
    try:
        settings = Settings.from_env()
        # print("******************** settings variable after going to config.py --> Settings class --> from_env method")
        # print(settings)

        # '''
        # settings sample value:
        # Settings(raw_data_dir=PosixPath('data/raw'), log_level='INFO', timeout_seconds=20.0, max_retries=4, backoff_base_seconds=0.75, forecast_days=7, locations=('Toronto', 'Milton', 'Ottawa', 'Windsor'))
        
        # '''


     
        if args.locations:
        #    if user specified a location other than the default, then convert it to a tuple and add it to 'settings' variable
            locations = tuple(part.strip() for part in args.locations.split(",") if part.strip())
            if not locations:
                parser.error("--locations must include at least one location")
            settings = Settings(**{**settings.__dict__, "locations": locations}) 
        if args.forecast_days is not None:
            if not 1 <= args.forecast_days <= 16:
                parser.error("--forecast-days must be between 1 and 16")
            settings = Settings(**{**settings.__dict__, "forecast_days": args.forecast_days})
        configure_logging(settings.log_level)


        # this is the where the primary part of the API calling is kicked off
        # run_ingestion belongs to ingest.py class which implements api_client.py which is the class responsible for actually making API calls
            # LEFT OFF HERE FOR TESTING
        manifest = run_ingestion(settings)
        failures = sum(record["status"] == "failed" for record in manifest["records"])
        print(json.dumps({
            "run_id": manifest["run_id"],
            "manifest": str(settings.raw_data_dir / f"run_id={manifest['run_id']}" / "manifest.json"),
            "records": len(manifest["records"]),
            "failures": failures,
        }, indent=2))
        return 1 if failures else 0
    except Exception as exc:
        logging.exception("ingestion_cli_failed")
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
