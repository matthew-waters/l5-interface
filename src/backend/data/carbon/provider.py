"""Provider interface for carbon intensity data sources."""

from __future__ import annotations

from typing import Protocol

from src.backend.data.carbon.types import CarbonActualRequest, CarbonForecastRequest
from src.models.carbon_intensity import CarbonIntensitySeries


class CarbonProvider(Protocol):
    """Provider interface to fetch carbon intensity data."""

    provider_id: str

    def supports_region(self, region: str) -> bool:
        """Return True if the provider can serve data for the given region."""

    def get_actual(self, request: CarbonActualRequest) -> CarbonIntensitySeries:
        """Return actual (historical/observed) carbon intensity series."""

    def get_forecast(self, request: CarbonForecastRequest) -> CarbonIntensitySeries:
        """Return forecast carbon intensity series."""

