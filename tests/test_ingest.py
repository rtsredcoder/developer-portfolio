import json
from datetime import datetime, timezone

from weather_ingestion.config import Settings
from weather_ingestion.ingest import run_ingestion


class FakeClient:
    def geocode(self, name):
        location = {
            "location_id": f"{name.lower()}-1-2", "name": name,
            "latitude": 1.0, "longitude": 2.0, "country": "Canada", "admin1": "Ontario"
        }
        return location, {"name": name, "count": 1}, 200

    def forecast(self, latitude, longitude, data_kind, forecast_days):
        return {"kind": data_kind, "forecast_days": forecast_days}, {
            "latitude": latitude, "longitude": longitude, data_kind: ["example"]
        }, 200


def test_ingestion_writes_manifest_and_preserves_runs(tmp_path):
    fixed = datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc)
    settings = Settings(raw_data_dir=tmp_path, locations=("Toronto", "Milton"))
    first = run_ingestion(settings, client=FakeClient(), now=lambda: fixed)
    second = run_ingestion(settings, client=FakeClient(), now=lambda: fixed)
    assert first["run_id"] != second["run_id"]
    run_dirs = list(tmp_path.glob("run_id=*"))
    assert len(run_dirs) == 2
    for run_dir in run_dirs:
        manifest = json.loads((run_dir / "manifest.json").read_text())
        assert len(manifest["records"]) == 6  # geocode + hourly + daily for each location
        assert all(item["status"] == "success" for item in manifest["records"])
        assert (run_dir / "toronto" / "hourly.json").exists()
        assert (run_dir / "toronto" / "daily.json").exists()
        assert json.loads((run_dir / "toronto" / "hourly.json").read_text())["kind"] == "hourly"


def test_failed_location_is_recorded_and_other_locations_continue(tmp_path):
    class PartialFailureClient(FakeClient):
        def geocode(self, name):
            if name == "Nowhere":
                raise RuntimeError("not found")
            return super().geocode(name)

    settings = Settings(raw_data_dir=tmp_path, locations=("Nowhere", "Milton"))
    manifest = run_ingestion(settings, client=PartialFailureClient())
    assert any(r["status"] == "failed" for r in manifest["records"])
    assert (tmp_path / f"run_id={manifest['run_id']}" / "milton" / "hourly.json").exists()
