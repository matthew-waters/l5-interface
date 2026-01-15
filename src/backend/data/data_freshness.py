"""Data freshness tracking for carbon intensity and spot fleet data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import NamedTuple


class DataFreshness(NamedTuple):
    """Represents the freshness of a data signal."""

    last_updated: datetime | None
    age_seconds: float | None

    def format_age(self) -> str:
        """Format the age in a human-readable way."""
        if self.last_updated is None or self.age_seconds is None:
            return "Never"

        age = timedelta(seconds=self.age_seconds)

        if age < timedelta(seconds=60):
            return f"{int(age.total_seconds())}s ago"
        elif age < timedelta(hours=1):
            return f"{int(age.total_seconds() / 60)}m ago"
        elif age < timedelta(days=1):
            return f"{int(age.total_seconds() / 3600)}h ago"
        else:
            return f"{int(age.days)}d ago"

    @property
    def is_stale(self) -> bool:
        """Check if data is considered stale (>1 hour old)."""
        if self.age_seconds is None:
            return True
        return self.age_seconds > 3600


class DataFreshnessTracker:
    """Tracks freshness of carbon intensity and spot fleet data."""

    def __init__(self) -> None:
        """Initialize the tracker."""
        self._carbon_last_updated: datetime | None = None
        self._availability_last_updated: datetime | None = None

    def update_carbon_freshness(self, timestamp: datetime | None = None) -> None:
        """Update the carbon intensity data freshness timestamp."""
        self._carbon_last_updated = timestamp or datetime.now(tz=timezone.utc)

    def update_availability_freshness(self, timestamp: datetime | None = None) -> None:
        """Update the spot fleet availability data freshness timestamp."""
        self._availability_last_updated = timestamp or datetime.now(tz=timezone.utc)

    def get_carbon_freshness(self) -> DataFreshness:
        """Get the current carbon intensity data freshness."""
        now = datetime.now(tz=timezone.utc)
        age_seconds = (
            (now - self._carbon_last_updated).total_seconds()
            if self._carbon_last_updated
            else None
        )
        return DataFreshness(
            last_updated=self._carbon_last_updated,
            age_seconds=age_seconds,
        )

    def get_availability_freshness(self) -> DataFreshness:
        """Get the current spot fleet availability data freshness."""
        now = datetime.now(tz=timezone.utc)
        age_seconds = (
            (now - self._availability_last_updated).total_seconds()
            if self._availability_last_updated
            else None
        )
        return DataFreshness(
            last_updated=self._availability_last_updated,
            age_seconds=age_seconds,
        )


# Global instance
_freshness_tracker = DataFreshnessTracker()


def get_freshness_tracker() -> DataFreshnessTracker:
    """Get the global data freshness tracker instance."""
    return _freshness_tracker