# Weather ingestion

A small, repeatable CLI for storing immutable raw hourly and daily forecast responses from Open-Meteo. It uses no database or API key; Docker Compose is provided to run the ingestion container with a persistent host directory.

## Project layout

```text
weather-ingestion/
├── src/weather_ingestion/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config.py
│   ├── ingest.py
│   └── cli.py
├── tests/
│   ├── test_api_client.py
│   └── test_ingest.py
├── data/raw/                 # generated, not committed
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Run locally (Python 3.11+)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# Linux / WSL:
source .venv/bin/activate

python -m pip install -e ".[dev]"
cp .env.example .env
# Windows PowerShell alternative: Copy-Item .env.example .env
weather-ingest
```

Override locations or settings as needed:

```bash
weather-ingest --locations Toronto,Milton,Ottawa,Windsor
weather-ingest --locations Toronto,Ottawa --forecast-days 3
pytest
```

## Run with Docker Compose

```bash
cp .env.example .env
docker compose run --rm weather-ingestion
```

Raw files persist in `./data/raw` on the host. There is no database service because the requested deliverable is raw ingestion only.

## Storage contract

Each execution gets a unique UTC run ID and a separate folder:

```text
data/raw/
└── run_id=20261026T104500123456Z/
    ├── manifest.json
    ├── toronto/
    │   ├── geocoding.json
    │   ├── hourly.json
    │   └── daily.json
    └── milton/
        ├── geocoding.json
        ├── hourly.json
        └── daily.json
```

The original successful API response bodies are saved as JSON without transforming their weather fields. Hourly and daily responses are separate forecast requests so each artifact clearly records its endpoint and request parameters. `manifest.json` records the UTC ingestion time, run ID, location ID/name/coordinates, source endpoint, request parameters, artifact path, status, and HTTP status where available. A failed request is logged and represented in the manifest; successful artifacts from the same run are retained.

A new run always writes to a new directory. A high-resolution UTC run ID plus exclusive directory creation prevents accidental overwrites. Do not manually reuse a run ID.

## Reliability behavior

- Connect/read timeout configured with `REQUEST_TIMEOUT_SECONDS`.
- Retry on connection/timeouts, HTTP 429, and 5xx responses, with exponential backoff and jitter.
- Other HTTP 4xx responses fail immediately.
- Structured JSON logs to stdout/stderr.
- Environment-based configuration and `.env` support.
- Tests mock HTTP calls; tests do not require network access.

## Notes

- Geocoding uses the first Open-Meteo geocoding match. Review the resolved name, region, and country in `geocoding.json` / `manifest.json` if place names are ambiguous.
- Forecast data is time-varying, so repeated runs intentionally preserve each response rather than deduplicating payloads.
