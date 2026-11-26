"""Schema/client and collector regression tests for new read-only artifacts."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
import collector
from sdk.python.pro_desk_telemetry import TelemetryClient
from sdk.action_server import risk_result
from tests.test_collector import tok


def test_time_window_snapshots_are_idempotent_and_keep_legacy_entries(tmp_path):
    path = str(tmp_path / "rows.jsonl")
    collector.collect(lambda m: tok(m), ["MINT"], path, now=0)
    assert collector.score_snapshots(lambda m: tok(m, liq=50_000), path, now=30 * 60) == 1
    assert collector.score_snapshots(lambda m: tok(m, liq=50_000), path, now=31 * 60) == 0
    rows = collector.load(path)
    snap = next(r for r in rows if r["kind"] == "snapshot")
    assert snap["window_min"] == 30 and snap["lp_delta_pct"] == -50
    assert "holder_metric_note" in snap


def test_python_sdk_schema_and_cache():
    calls = []
    client = TelemetryClient("https://example.invalid/api", fetcher=lambda url: calls.append(url) or {"schema": "1.0", "features": []})
    assert client.features() == client.features() and len(calls) == 1


def test_action_endpoint_returns_only_local_informational_data(tmp_path):
    ds, sm = tmp_path / "dataset.json", tmp_path / "summary.json"
    ds.write_text(json.dumps({"schema": "1.0", "rows": []}))
    sm.write_text(json.dumps({"edge_status": "INSUFFICIENT_DATA"}))
    assert risk_result("invalid", ds, sm)["error"] == "invalid_mint"
    assert risk_result("11111111111111111111111111111111", ds, sm)["error"] == "not_found"
