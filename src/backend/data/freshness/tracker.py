"""Facade tracker that composes per-provider freshness trackers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from src.backend.data.freshness.base import DataFreshness
from src.backend.data.freshness.fleet import FleetFreshnessTracker
from src.backend.data.freshness.neso import NesoFreshnessTracker
from src.backend.data.freshness.watttime import WattTimeFreshnessTracker

if TYPE_CHECKING:
    from src.backend.data.fleet.api_client import SpotFleetAPIClient


class DataFreshnessTracker:
    """Tracks freshness of NESO, WattTime, and Spot Fleet signals."""

    def __init__(self, api_client: SpotFleetAPIClient | None = None) -> None:
        self._neso = NesoFreshnessTracker()
        self._wt = WattTimeFreshnessTracker()
        self._fleet = FleetFreshnessTracker(api_client=api_client)

    # --- NESO ---
    def update_neso_freshness(self, timestamp: datetime | None = None) -> None:
        self._neso.update(timestamp)

    def refresh_neso_freshness_from_api(self) -> bool:
        return self._neso.refresh_from_api()

    def get_neso_freshness(self) -> DataFreshness:
        return self._neso.get()

    # --- WattTime ---
    def update_wt_freshness(self, timestamp: datetime | None = None) -> None:
        self._wt.update(timestamp)

    def refresh_wt_freshness_from_api(self) -> bool:
        return self._wt.refresh_from_api()

    def get_wt_freshness(self) -> DataFreshness:
        return self._wt.get()

    # --- Fleet ---
    def update_availability_freshness(self, timestamp: datetime | None = None) -> None:
        self._fleet.update(timestamp)

    def refresh_availability_freshness_from_api(self) -> bool:
        return self._fleet.refresh_from_api()

    def get_availability_freshness(self) -> DataFreshness:
        return self._fleet.get()

    # --- Legacy / convenience ---
    def update_carbon_freshness(self, timestamp: datetime | None = None) -> None:
        """Legacy: update both carbon sources as 'refreshed'."""
        self.update_neso_freshness(timestamp)
        self.update_wt_freshness(timestamp)

    def get_carbon_freshness(self) -> DataFreshness:
        """Legacy: return the freshest (most recently updated) of NESO/WT."""
        neso_ts = self._neso.get().last_updated
        wt_ts = self._wt.get().last_updated
        candidates = [t for t in (neso_ts, wt_ts) if t is not None]
        return DataFreshness(last_updated=max(candidates) if candidates else None)


# Global singleton (centralized here, alongside the concrete tracker implementation).
_freshness_tracker = DataFreshnessTracker()


def get_freshness_tracker() -> DataFreshnessTracker:
    """Get the global data freshness tracker instance."""
    return _freshness_tracker

