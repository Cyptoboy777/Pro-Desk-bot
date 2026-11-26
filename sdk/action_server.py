"""Minimal stdlib HTTP reference server for read-only risk inspection.

GET /api/v1/actions/risk-check?mint=<address> returns informational JSON only.
No transaction, wallet, signing or fund-transfer route exists.
"""
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE = Path(__file__).resolve().parents[1]


def risk_result(mint, dataset_path=None, summary_path=None):
    if not isinstance(mint, str) or not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{32,44}", mint):
        return {"error": "invalid_mint", "message": "Provide a base58 token mint address."}
    ds_path = Path(dataset_path or BASE / "docs/api/v1/dataset.json")
    sm_path = Path(summary_path or BASE / "docs/api/v1/summary.json")
    try:
        rows = json.loads(ds_path.read_text()).get("rows", [])
        summary = json.loads(sm_path.read_text())
    except (OSError, ValueError):
        return {"error": "data_unavailable", "message": "Published telemetry data is not available."}
    row = next((r for r in rows if r.get("mint") == mint), None)
    if row is None:
        return {"error": "not_found", "mint": mint, "message": "Mint is not in this recorded dataset; no live claim is made."}
    from desk.risk_engine import assess
    verdict = assess(row)
    return {"schema": "1.0", "mint": mint, "risk_score": verdict["risk_score"], "passed_rubric": verdict["passed"],
            "failed_reasons": verdict["failed_reasons"], "first_seen": row.get("ts"), "bad_24h": row.get("bad_24h"),
            "historical_survival_benchmark": summary.get("pass_vs_reject_24h"),
            "benchmark_status": summary.get("edge_status"),
            "disclaimer": "Empirical, sample-limited informational data only; not a safety guarantee or trading recommendation."}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/actions.json":
            body, status = {"rules": [], "hosts": ["cyptoboy777.github.io"], "version": 1}, 200
        elif parsed.path == "/api/v1/actions/risk-check":
            mint = parse_qs(parsed.query).get("mint", [""])[0]
            body = risk_result(mint)
            status = 200 if "error" not in body else (400 if body["error"] == "invalid_mint" else 404)
        else:
            body, status = {"error": "not_found"}, 404
        raw = json.dumps(body).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(raw)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8080)
    a = p.parse_args(); print(f"Read-only inspection server at http://{a.host}:{a.port}")
    HTTPServer((a.host, a.port), Handler).serve_forever()
