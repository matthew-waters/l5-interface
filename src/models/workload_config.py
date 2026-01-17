"""Workload configuration (draft) model for the Create Workload wizard.

This is intentionally separate from `src.models.workload.Workload`:
- `WorkloadConfig` represents an in-progress, user-editable draft (wizard state).
- `Workload` represents a submitted/scheduled workload (later lifecycle stages).

The config is JSON-first and versioned so it can be stored locally or remotely.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Self


class DelayTolerance(StrEnum):
    """Plain-English delay tolerance categories (extensible)."""

    NOT_DELAY_TOLERANT = "NOT_DELAY_TOLERANT"
    UP_TO_1_HOUR = "UP_TO_1_HOUR"
    UP_TO_6_HOURS = "UP_TO_6_HOURS"
    UP_TO_24_HOURS = "UP_TO_24_HOURS"

    def label(self) -> str:
        return {
            DelayTolerance.NOT_DELAY_TOLERANT: "Not delay-tolerant",
            DelayTolerance.UP_TO_1_HOUR: "Up to 1 hour",
            DelayTolerance.UP_TO_6_HOURS: "Up to 6 hours",
            DelayTolerance.UP_TO_24_HOURS: "Up to 24 hours",
        }[self]


class RuntimeEstimateSource(StrEnum):
    """Where the runtime estimate came from."""

    MANUAL = "MANUAL"
    PROFILED = "PROFILED"  # placeholder for later


@dataclass(frozen=True, slots=True)
class WorkloadConfig:
    """Draft workload configuration (wizard state)."""

    version: int
    config_id: str

    created_at: datetime
    updated_at: datetime

    # ---- Stage 2.1: workload definition ----
    name: str = ""
    description: str = ""

    # ---- Stage 2.2: job specification (partial for now) ----
    interruptible: bool | None = None
    delay_tolerance: DelayTolerance | None = None

    # ---- Stage 2.3: hardware selection + runtime ----
    fleet_id: int | None = None
    fleet_name: str | None = None
    fleet_region: str | None = None
    fleet_instance_types: list[str] | None = None
    fleet_target_capacities: list[int] | None = None
    fleet_metadata: dict[str, Any] | None = None

    runtime_estimate_seconds: int | None = None
    runtime_estimate_source: RuntimeEstimateSource | None = None

    @staticmethod
    def _dt_to_iso(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def _dt_from_iso(value: str) -> datetime:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def touch(self) -> WorkloadConfig:
        """Return a copy with updated `updated_at`."""
        return replace(self, updated_at=datetime.now(tz=timezone.utc))

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self._dt_to_iso(self.created_at)
        data["updated_at"] = self._dt_to_iso(self.updated_at)

        if self.delay_tolerance is not None:
            data["delay_tolerance"] = self.delay_tolerance.value
        if self.runtime_estimate_source is not None:
            data["runtime_estimate_source"] = self.runtime_estimate_source.value

        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            version=int(data.get("version", 1)),
            config_id=str(data["config_id"]),
            created_at=cls._dt_from_iso(str(data["created_at"])),
            updated_at=cls._dt_from_iso(str(data["updated_at"])),
            name=str(data.get("name", "") or ""),
            description=str(data.get("description", "") or ""),
            interruptible=(
                bool(data["interruptible"]) if data.get("interruptible") is not None else None
            ),
            delay_tolerance=(
                DelayTolerance(str(data["delay_tolerance"]))
                if data.get("delay_tolerance") is not None
                else None
            ),
            fleet_id=(int(data["fleet_id"]) if data.get("fleet_id") is not None else None),
            fleet_name=(str(data["fleet_name"]) if data.get("fleet_name") is not None else None),
            fleet_region=(
                str(data["fleet_region"]) if data.get("fleet_region") is not None else None
            ),
            fleet_instance_types=(
                list(data["fleet_instance_types"])
                if data.get("fleet_instance_types") is not None
                else None
            ),
            fleet_target_capacities=(
                [int(x) for x in data["fleet_target_capacities"]]
                if data.get("fleet_target_capacities") is not None
                else None
            ),
            fleet_metadata=(
                dict(data["fleet_metadata"]) if data.get("fleet_metadata") is not None else None
            ),
            runtime_estimate_seconds=(
                int(data["runtime_estimate_seconds"])
                if data.get("runtime_estimate_seconds") is not None
                else None
            ),
            runtime_estimate_source=(
                RuntimeEstimateSource(str(data["runtime_estimate_source"]))
                if data.get("runtime_estimate_source") is not None
                else None
            ),
        )

