from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    raw_data_dir: Path
    log_level: str = "INFO"
    timeout_seconds: float = 20.0
    max_retries: int = 4
    backoff_base_seconds: float = 0.75
    forecast_days: int = 7
    locations: tuple[str, ...] = ("Toronto", "Milton", "Ottawa", "Windsor")

    @classmethod
    def from_env(cls) -> "Settings":
        print("*************** in config.py --> Settings class --> from_env method")
        load_dotenv()

        # print("os.getenv(LOCATIONS)")
        # print(os.getenv("LOCATIONS"))

        # convert locations value from .env file into a tuple --> ('Toronto', 'Milton', 'Ottawa', 'Windsor')
        locations = tuple(
            item.strip()
            for item in os.getenv("LOCATIONS", "Toronto,Milton,Ottawa,Windsor").split(",")
            if item.strip()
        )

        # print("************** locations")
        # print(locations)
        
        if not locations:
            raise ValueError("LOCATIONS must contain at least one location")
        
        settings = cls(
            raw_data_dir=Path(os.getenv("RAW_DATA_DIR", "data/raw")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
            max_retries=int(os.getenv("MAX_RETRIES", "4")),
            backoff_base_seconds=float(os.getenv("BACKOFF_BASE_SECONDS", "0.75")),
            forecast_days=int(os.getenv("FORECAST_DAYS", "7")),
            locations=locations,
        )
        if settings.timeout_seconds <= 0:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be greater than zero")
        if settings.max_retries < 0:
            raise ValueError("MAX_RETRIES cannot be negative")
        if settings.backoff_base_seconds < 0:
            raise ValueError("BACKOFF_BASE_SECONDS cannot be negative")
        if not 1 <= settings.forecast_days <= 16:
            raise ValueError("FORECAST_DAYS must be between 1 and 16")
        return settings
