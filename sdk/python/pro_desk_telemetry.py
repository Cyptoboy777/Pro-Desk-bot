"""Zero-dependency read-only client for the published Pro Desk telemetry API (GET requests only, no wallet code)."""
from __future__ import annotations
import json
import time
from typing import Any, Callable
from urllib.request import urlopen

DEFAULT_BASE_URL = "https://cyptoboy777.github.io/Pro-Desk-bot/api/v1/"
NEEDS_SCHEMA = {"summary", "features", "recent_scans", "rubric", "dataset"}
RESOURCES = ("summary", "features", "recent_scans", "rubric", "dataset", "actions")


def _check(name: str, v: dict) -> str | None:
    if name == "summary":
        return "missing pass_vs_reject_24h" if not isinstance(v.get("pass_vs_reject_24h"), dict) else (
            "missing edge_status" if not isinstance(v.get("edge_status"), str) else None)
    if name == "features":
        return None if isinstance(v.get("features"), list) else "features must be a list"
    if name == "recent_scans":
        return None if isinstance(v.get("scans"), list) else "scans must be a list"
    if name == "rubric":
        return None if isinstance(v.get("config"), dict) else "missing config"
    if name == "dataset":
        return None if isinstance(v.get("rows"), list) else "rows must be a list"
    return None if isinstance(v.get("rules"), list) else "rules must be a list"


def validate(name: str, value: Any) -> dict:
    """Return `value` if it has the right shape for resource `name`, else raise ValueError."""
    if name not in RESOURCES:
        raise ValueError("unsupported telemetry resource")
    if not isinstance(value, dict):
        raise ValueError("invalid telemetry JSON shape")
    if name in NEEDS_SCHEMA and "schema" not in value:
        raise ValueError("invalid telemetry JSON shape: missing schema")
    err = _check(name, value)
    if err:
        raise ValueError("invalid telemetry JSON shape: " + err)
    return value


class TelemetryClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, ttl_seconds: float = 60, fetcher: Callable | None = None):
        self.base_url = base_url.rstrip("/") + "/"
        self.ttl_seconds = ttl_seconds
        self._fetcher = fetcher or self._read
        self._cache: dict[str, tuple[float, Any]] = {}

    def _read(self, url: str) -> Any:
        with urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def get(self, name: str) -> dict:
        if name not in RESOURCES:
            raise ValueError("unsupported telemetry resource")
        now = time.monotonic()
        cached = self._cache.get(name)
        if cached and now - cached[0] < self.ttl_seconds:
            return cached[1]
        value = validate(name, self._fetcher(self.base_url + name + ".json"))
        self._cache[name] = (now, value)
        return value

    def clear_cache(self) -> None: self._cache.clear()
    def get_summary(self) -> dict: return self.get("summary")
    def get_features(self) -> dict: return self.get("features")
    def get_recent_scans(self) -> dict: return self.get("recent_scans")
    def get_rubric(self) -> dict: return self.get("rubric")
    def get_dataset(self) -> dict: return self.get("dataset")
    def get_actions(self) -> dict: return self.get("actions")
    def summary(self) -> dict: return self.get_summary()
    def features(self) -> dict: return self.get_features()
    def dataset(self) -> dict: return self.get_dataset()
