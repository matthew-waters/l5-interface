"""WattTime provider (skeleton)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.backend.data.carbon.conversions import LBS_TO_GRAMS, MWH_TO_KWH
from src.backend.data.carbon.types import CarbonActualRequest, CarbonForecastRequest, normalize_region
from src.models.carbon_intensity import (
    CarbonIntensityKind,
    CarbonIntensityPoint,
    CarbonIntensitySeries,
)


class WattTimeCarbonProvider:
    """WattTime carbon intensity provider.

    Notes:
    - API integration is intentionally not implemented yet.
    - Mapping helpers mirror your TS project (lbs/MWh → g/kWh conversion).
    """

    provider_id = "watttime"

    def supports_region(self, region: str) -> bool:
        # Assume WattTime covers non-GB regions by default.
        return normalize_region(region) not in {"GB", "UK", "GBR", "GREAT_BRITAIN"}

    def get_actual(self, request: CarbonActualRequest) -> CarbonIntensitySeries:
        # Placeholder: return empty series until API fetch is implemented.
        return CarbonIntensitySeries(
            points=[],
            provider_id=self.provider_id,
            kind=CarbonIntensityKind.ACTUAL,
            region=normalize_region(request.region),
        )

    def get_forecast(self, request: CarbonForecastRequest) -> CarbonIntensitySeries:
        # Placeholder: return empty series until API fetch is implemented.
        return CarbonIntensitySeries(
            points=[],
            provider_id=self.provider_id,
            kind=CarbonIntensityKind.FORECAST,
            region=normalize_region(request.region),
        )


def map_watttime_historical(payload: dict[str, Any]) -> list[CarbonIntensityPoint]:
    """Map WattTime historical payload to points (lbs/MWh → g/kWh)."""

    points: list[CarbonIntensityPoint] = []
    for item in payload.get("data", []) or []:
        value = item.get("value")
        if value is None:
            continue
        ts = datetime.fromisoformat(str(item["point_time"]))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        g_per_kwh = (float(value) * LBS_TO_GRAMS) / MWH_TO_KWH
        points.append(CarbonIntensityPoint(timestamp=ts, value_g_per_kwh=g_per_kwh))
    return points


def map_watttime_forecast(payload: dict[str, Any]) -> list[CarbonIntensityPoint]:
    """Map WattTime forecast payload to points (lbs/MWh → g/kWh)."""

    # Some WattTime forecast responses include a leading point that you trimmed in TS.
    data = list(payload.get("data", []) or [])
    if len(data) > 1:
        data = data[1:]

    points: list[CarbonIntensityPoint] = []
    for item in data:
        value = item.get("value")
        if value is None:
            continue
        ts = datetime.fromisoformat(str(item["point_time"]))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        g_per_kwh = (float(value) * LBS_TO_GRAMS) / MWH_TO_KWH
        points.append(CarbonIntensityPoint(timestamp=ts, value_g_per_kwh=g_per_kwh))
    return points

