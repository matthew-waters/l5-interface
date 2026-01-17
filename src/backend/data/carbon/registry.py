"""Provider selection / registry for carbon intensity."""

from __future__ import annotations

from src.backend.data.carbon.provider import CarbonProvider
from src.backend.data.carbon.types import normalize_region


def get_provider_for_region(region: str) -> CarbonProvider:
    """Select a carbon provider based on region (per-region strategy).

    Examples:
    - GB / UK -> UK Grid / Carbon Intensity API GB
    - otherwise -> WattTime (default)
    """

    # Local imports to avoid importing provider modules at import time.
    from src.backend.data.carbon.providers.uk_grid import UKGridCarbonProvider
    from src.backend.data.carbon.providers.watttime import WattTimeCarbonProvider

    region_norm = normalize_region(region)

    uk = UKGridCarbonProvider()
    if uk.supports_region(region_norm):
        return uk

    # Default provider (assumed broadest coverage).
    return WattTimeCarbonProvider()

