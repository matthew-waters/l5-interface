"""Carbon intensity data access and refresh.

This module provides a provider-agnostic service for fetching:
- actual (historical/observed) carbon intensity
- forecast carbon intensity

Provider selection is handled per-region via `src.backend.data.carbon.registry`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.backend.data.carbon.registry import get_provider_for_region
from src.backend.data.carbon.types import CarbonActualRequest, CarbonForecastRequest
from src.backend.data.data_freshness import get_freshness_tracker
from src.models.carbon_intensity import CarbonIntensitySeries


class CarbonDataService:
    """Provider-agnostic facade for carbon intensity data."""

    def get_actual(
        self,
        *,
        region: str,
        start: datetime,
        end: datetime,
    ) -> CarbonIntensitySeries:
        provider = get_provider_for_region(region)
        series = provider.get_actual(CarbonActualRequest(region=region, start=start, end=end))

        # Mark carbon data as refreshed (even if the series is empty for now).
        get_freshness_tracker().update_carbon_freshness(datetime.now(tz=timezone.utc))
        return series

    def get_forecast(
        self,
        *,
        region: str,
        start: datetime | None = None,
        horizon: timedelta = timedelta(hours=48),
    ) -> CarbonIntensitySeries:
        start_dt = start or datetime.now(tz=timezone.utc)
        provider = get_provider_for_region(region)
        series = provider.get_forecast(
            CarbonForecastRequest(region=region, start=start_dt, horizon=horizon)
        )

        # Mark carbon data as refreshed (even if the series is empty for now).
        get_freshness_tracker().update_carbon_freshness(datetime.now(tz=timezone.utc))
        return series

