"""Freshness tracker for Spot Fleet availability data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from src.backend.data.freshness.base import DataFreshness

if TYPE_CHECKING:
    from src.backend.data.fleet.api_client import SpotFleetAPIClient


class FleetFreshnessTracker:
    """Tracks freshness of Spot Fleet availability data."""

    def __init__(self, api_client: SpotFleetAPIClient | None = None) -> None:
        self._last_updated: datetime | None = None
        self._api_client = api_client

    def update(self, timestamp: datetime | None = None) -> None:
        # Important: don't overwrite a previously-known freshness timestamp with None.
        # Spot Fleet UI flows may make API calls that don't include any time-series
        # datapoint; those should not reset freshness to "N/A".
        if timestamp is None:
            return
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        self._last_updated = timestamp

    def get(self) -> DataFreshness:
        return DataFreshness(last_updated=self._last_updated)

    def check_from_api(self) -> datetime | None:
        """Determine last updated time from the Spot Fleet API."""
        # Lazy import to avoid circular dependency
        from src.backend.data.fleet.api_client import SpotFleetAPIClient

        try:
            api_client = self._api_client or SpotFleetAPIClient()
            fleets = api_client.get_request_groups()
            if not fleets:
                return None
            latest_scores = api_client.get_latest_placement_scores(fleets[0].id)
            if not latest_scores:
                return None
            return max(score.measured_at for score in latest_scores)
        except Exception:
            return None

    def refresh_from_api(self) -> bool:
        ts = self.check_from_api()
        if ts is None:
            return False
        self.update(ts)
        return True

