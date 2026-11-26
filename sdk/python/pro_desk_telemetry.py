"""Zero-dependency read-only client for the published Pro Desk telemetry API."""
from __future__ import annotations
import json
import time
from typing import Any, Callable
from urllib.request import urlopen

DEFAULT_BASE_URL = "https://cyptoboy777.github.io/Pro-Desk-bot/api/v1/"

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
        if name not in {"summary", "features", "dataset", "recent_scans", "rubric"}:
            raise ValueError("unsupported telemetry resource")
        now = time.monotonic()
        cached = self._cache.get(name)
        if cached and now - cached[0] < self.ttl_seconds:
            return cached[1]
        value = self._fetcher(self.base_url + name + ".json")
        if not isinstance(value, dict) or "schema" not in value:
            raise ValueError("invalid telemetry JSON shape")
        self._cache[name] = (now, value)
        return value

    def summary(self) -> dict: return self.get("summary")
    def features(self) -> dict: return self.get("features")
    def dataset(self) -> dict: return self.get("dataset")
