"""Shared freshness model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True, slots=True)
class DataFreshness:
    """Represents the freshness of a data signal."""

    last_updated: datetime | None
    stale_after_seconds: int = 3600

    def format_age(self) -> str:
        """Format the age in a human-readable way."""
        if self.last_updated is None:
            return "N/A"

        age_seconds = self.age_seconds
        if age_seconds is None:
            return "N/A"

        age = timedelta(seconds=age_seconds)

        if age < timedelta(seconds=60):
            return f"{int(age.total_seconds())}s ago"
        if age < timedelta(hours=1):
            return f"{int(age.total_seconds() / 60)}m ago"
        if age < timedelta(days=1):
            return f"{int(age.total_seconds() / 3600)}h ago"
        return f"{int(age.days)}d ago"

    @property
    def age_seconds(self) -> float | None:
        if self.last_updated is None:
            return None
        now = datetime.now(tz=timezone.utc)
        try:
            return (now - self.last_updated).total_seconds()
        except Exception:
            return None

    @property
    def is_stale(self) -> bool:
        """Check if data is considered stale."""
        age = self.age_seconds
        if age is None:
            return True
        return age > self.stale_after_seconds

