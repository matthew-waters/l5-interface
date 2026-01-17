"""Carbon intensity time-series models (provider-agnostic)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self


class CarbonIntensityKind(StrEnum):
    ACTUAL = "actual"
    FORECAST = "forecast"


class CarbonIntensityUnits(StrEnum):
    """Normalized units for carbon intensity values."""

    GCO2_PER_KWH = "gCO2/kWh"


@dataclass(frozen=True, slots=True)
class CarbonIntensityPoint:
    """A single carbon intensity measurement/forecast point."""

    timestamp: datetime
    value_g_per_kwh: float

    @staticmethod
    def _dt_to_iso(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def _dt_from_iso(value: str) -> datetime:
        return datetime.fromisoformat(value)

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self._dt_to_iso(self.timestamp)
        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=cls._dt_from_iso(str(data["timestamp"])),
            value_g_per_kwh=float(data["value_g_per_kwh"]),
        )


@dataclass(frozen=True, slots=True)
class CarbonIntensitySeries:
    """A normalized carbon intensity series in gCO₂/kWh."""

    points: list[CarbonIntensityPoint]
    provider_id: str
    kind: CarbonIntensityKind
    region: str
    units: CarbonIntensityUnits = CarbonIntensityUnits.GCO2_PER_KWH

    def to_json(self) -> dict[str, Any]:
        return {
            "points": [p.to_json() for p in self.points],
            "provider_id": self.provider_id,
            "kind": self.kind.value,
            "region": self.region,
            "units": self.units.value,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            points=[CarbonIntensityPoint.from_json(p) for p in data.get("points", [])],
            provider_id=str(data["provider_id"]),
            kind=CarbonIntensityKind(str(data["kind"])),
            region=str(data["region"]),
            units=CarbonIntensityUnits(str(data.get("units", CarbonIntensityUnits.GCO2_PER_KWH.value))),
        )

