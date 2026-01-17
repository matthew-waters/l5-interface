"""Freshness tracker for NESO / UK Grid (Carbon Intensity API GB)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.backend.data.freshness.base import DataFreshness


class NesoFreshnessTracker:
    """Tracks freshness for NESO (Carbon Intensity API GB)."""

    def __init__(self) -> None:
        self._last_updated: datetime | None = None

    def update(self, timestamp: datetime | None = None) -> None:
        self._last_updated = timestamp or datetime.now(tz=timezone.utc)

    def get(self) -> DataFreshness:
        return DataFreshness(last_updated=self._last_updated)

    def check_from_api(self) -> datetime | None:
        """Return a representative timestamp from the API response."""
        import requests
        from dateutil.parser import isoparse

        try:
            url = "https://api.carbonintensity.org.uk/intensity"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            items = payload.get("data", []) or []
            if not items:
                return None

            raw_ts = items[0].get("to") or items[0].get("from")
            if not raw_ts:
                return None

            ts = isoparse(str(raw_ts))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts
        except Exception:
            return None

    def refresh_from_api(self) -> bool:
        ts = self.check_from_api()
        if ts is None:
            return False
        self.update(ts)
        return True

