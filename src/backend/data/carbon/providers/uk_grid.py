"""UK Grid / Carbon Intensity API (Great Britain) provider (skeleton)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.backend.data.carbon.types import CarbonActualRequest, CarbonForecastRequest, normalize_region
from src.models.carbon_intensity import (
    CarbonIntensityKind,
    CarbonIntensityPoint,
    CarbonIntensitySeries,
)


class UKGridCarbonProvider:
    """Carbon Intensity API Great Britain provider.

    Notes:
    - API integration is intentionally not implemented yet.
    - Mapping helpers mirror your TS project (actual uses `intensity.actual`, forecast uses `intensity.forecast`).
    """

    # Display/provider id used in freshness/UI ("NESO" UK grid).
    provider_id = "neso"

    def supports_region(self, region: str) -> bool:
        r = normalize_region(region)
        return r in {"GB", "UK", "GBR", "GREAT_BRITAIN"}

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


def map_gb_actual(payload: dict[str, Any]) -> list[CarbonIntensityPoint]:
    """Map Carbon Intensity GB payload to points (actual)."""

    points: list[CarbonIntensityPoint] = []
    for item in payload.get("data", []) or []:
        intensity = item.get("intensity") or {}
        actual = intensity.get("actual")
        if actual is None:
            continue
        # The API uses ISO timestamps; we treat them as UTC if naive.
        ts = datetime.fromisoformat(str(item["to"]))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        points.append(CarbonIntensityPoint(timestamp=ts, value_g_per_kwh=float(actual)))
    return points


def map_gb_forecast(payload: dict[str, Any]) -> list[CarbonIntensityPoint]:
    """Map Carbon Intensity GB payload to points (forecast)."""

    points: list[CarbonIntensityPoint] = []
    for item in payload.get("data", []) or []:
        intensity = item.get("intensity") or {}
        forecast = intensity.get("forecast")
        if forecast is None:
            continue
        ts = datetime.fromisoformat(str(item["to"]))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        points.append(CarbonIntensityPoint(timestamp=ts, value_g_per_kwh=float(forecast)))
    return points

