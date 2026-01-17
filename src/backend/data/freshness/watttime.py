"""Freshness tracker for WattTime."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.backend.data.freshness.base import DataFreshness


class WattTimeFreshnessTracker:
    """Tracks freshness for WattTime."""

    def __init__(self) -> None:
        self._last_updated: datetime | None = None

    def update(self, timestamp: datetime | None = None) -> None:
        self._last_updated = timestamp or datetime.now(tz=timezone.utc)

    def get(self) -> DataFreshness:
        return DataFreshness(last_updated=self._last_updated)

    @staticmethod
    def _load_local_credentials():
        from src.storage.config_store import ConfigStore

        repo_root = Path(__file__).resolve().parents[4]
        store = ConfigStore(repo_root / "data" / "configs")
        return store.load_credentials()

    def check_from_api(self) -> datetime | None:
        """Return most recent point_time from a small historical query."""
        import requests
        from dateutil.parser import isoparse

        from src.backend.data.carbon.auth.watttime_auth import get_watttime_token

        try:
            creds = self._load_local_credentials()
            token = get_watttime_token(creds)

            now = datetime.now(tz=timezone.utc)
            start = now - timedelta(hours=1)

            # TODO: make region/signal configurable (currently mirrors TS example defaults).
            url = "https://api.watttime.org/v3/historical"
            params = {
                "start": start.isoformat(),
                "end": now.isoformat(),
                "region": "CAISO_NORTH",
                "signal_type": "co2_moer",
            }
            headers = {"Authorization": f"Bearer {token}"}

            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            items = payload.get("data", []) or []
            if not items:
                return None

            ts = max(isoparse(str(item["point_time"])) for item in items if item.get("point_time"))
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

