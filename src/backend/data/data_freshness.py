"""Data freshness tracking for carbon intensity and spot fleet data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from src.backend.data.fleet.api_client import SpotFleetAPIClient


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

    def __init__(self, api_client: SpotFleetAPIClient | None = None) -> None:
        """Initialize the tracker.

        Args:
            api_client: Optional SpotFleetAPIClient instance for API queries.
                       Creates new one if not provided.
        """
        self._carbon_last_updated: datetime | None = None
        self._availability_last_updated: datetime | None = None
        self._api_client = api_client

    def update_carbon_freshness(self, timestamp: datetime | None = None) -> None:
        """Update the carbon intensity data freshness timestamp."""
        self._carbon_last_updated = timestamp or datetime.now(tz=timezone.utc)

    def update_availability_freshness(self, timestamp: datetime | None = None) -> None:
        """Update the spot fleet availability data freshness timestamp.
        """
        if timestamp is None:
            self._availability_last_updated = None
            return

        # Normalize naive datetimes to UTC; keep aware datetimes as-is.
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        self._availability_last_updated = timestamp

    def check_availability_freshness_from_api(self) -> datetime | None:
        """Check the actual data freshness from the Spot Fleet API.

        Queries the latest placement scores endpoint to determine when
        the data was last updated on the server side.

        Returns:
            The most recent measured_at timestamp from the API, or None if
            the check fails (e.g., API unavailable, no data available).

        Note:
            This method does NOT update the internal freshness timestamp.
            Call update_availability_freshness() with the returned timestamp
            if you want to update it.
        """

        # Lazy import to avoid circular dependency
        from src.backend.data.fleet.api_client import SpotFleetAPIClient

        try:
            # Use provided client or create new one
            api_client = self._api_client or SpotFleetAPIClient()

            # Get the first available request group
            fleets = api_client.get_request_groups()
            if not fleets:
                return None

            # Get latest placement scores for the first fleet
            # This gives us the most recent measured_at timestamp
            latest_scores = api_client.get_latest_placement_scores(fleets[0].id)
            if not latest_scores:
                return None

            # Find the most recent measured_at timestamp
            most_recent = max(score.measured_at for score in latest_scores)
            return most_recent

        except Exception:
            # If API call fails, return None (don't update freshness)
            # This allows the system to continue working even if API is unavailable
            return None

    def refresh_availability_freshness_from_api(self) -> bool:
        """Check API for freshness and update the internal timestamp.

        Convenience method that calls check_availability_freshness_from_api()
        and updates the internal freshness timestamp if a timestamp is returned.

        Returns:
            True if freshness was successfully updated from API, False otherwise.
        """

        api_timestamp = self.check_availability_freshness_from_api()
        if api_timestamp is not None:
            self.update_availability_freshness(api_timestamp)
            return True
        return False

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