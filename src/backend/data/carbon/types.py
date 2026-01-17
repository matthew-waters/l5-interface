"""Provider-agnostic request/response types for carbon intensity data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True, slots=True)
class CarbonActualRequest:
    """Request for actual (historical / observed) carbon intensity data."""

    region: str
    start: datetime
    end: datetime


@dataclass(frozen=True, slots=True)
class CarbonForecastRequest:
    """Request for forecast carbon intensity data."""

    region: str
    start: datetime
    horizon: timedelta


def normalize_region(region: str) -> str:
    """Normalize region identifiers for provider selection."""
    return region.strip().upper()

