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
    deadline_at: datetime | None = None
    earliest_start_at: datetime | None = None

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
        return {
            "meta": {
                "version": self.version,
                "config_id": self.config_id,
                "created_at": self._dt_to_iso(self.created_at),
                "updated_at": self._dt_to_iso(self.updated_at),
            },
            "general": {
                "name": self.name,
                "description": self.description,
            },
            "job_semantics": {
                "interruptible": self.interruptible,
                "delay_tolerance": (
                    self.delay_tolerance.value if self.delay_tolerance is not None else None
                ),
                "runtime_bounds": {
                    "deadline_at": (
                        self._dt_to_iso(self.deadline_at) if self.deadline_at is not None else None
                    ),
                    "earliest_start_at": (
                        self._dt_to_iso(self.earliest_start_at)
                        if self.earliest_start_at is not None
                        else None
                    ),
                },
            },
            "hardware": {
                "fleet": {
                    "id": self.fleet_id,
                    "name": self.fleet_name,
                    "region": self.fleet_region,
                    "instance_types": self.fleet_instance_types,
                    "target_capacities": self.fleet_target_capacities,
                    "metadata": self.fleet_metadata,
                },
            },
            "runtime_estimate": {
                "seconds": self.runtime_estimate_seconds,
                "source": (
                    self.runtime_estimate_source.value
                    if self.runtime_estimate_source is not None
                    else None
                ),
            },
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        meta = dict(data.get("meta") or {})
        general = dict(data.get("general") or {})
        job_semantics = dict(data.get("job_semantics") or {})
        runtime_bounds = dict(job_semantics.get("runtime_bounds") or {})
        hardware = dict(data.get("hardware") or {})
        fleet = dict(hardware.get("fleet") or {})
        runtime_estimate = dict(data.get("runtime_estimate") or {})

        return cls(
            version=int(meta.get("version", 1)),
            config_id=str(meta["config_id"]),
            created_at=cls._dt_from_iso(str(meta["created_at"])),
            updated_at=cls._dt_from_iso(str(meta["updated_at"])),
            name=str(general.get("name", "") or ""),
            description=str(general.get("description", "") or ""),
            interruptible=(
                bool(job_semantics["interruptible"])
                if job_semantics.get("interruptible") is not None
                else None
            ),
            delay_tolerance=(
                DelayTolerance(str(job_semantics["delay_tolerance"]))
                if job_semantics.get("delay_tolerance") is not None
                else None
            ),
            deadline_at=(
                cls._dt_from_iso(str(runtime_bounds["deadline_at"]))
                if runtime_bounds.get("deadline_at") is not None
                else None
            ),
            earliest_start_at=(
                cls._dt_from_iso(str(runtime_bounds["earliest_start_at"]))
                if runtime_bounds.get("earliest_start_at") is not None
                else None
            ),
            fleet_id=(int(fleet["id"]) if fleet.get("id") is not None else None),
            fleet_name=(str(fleet["name"]) if fleet.get("name") is not None else None),
            fleet_region=(
                str(fleet["region"]) if fleet.get("region") is not None else None
            ),
            fleet_instance_types=(
                list(fleet["instance_types"])
                if fleet.get("instance_types") is not None
                else None
            ),
            fleet_target_capacities=(
                [int(x) for x in fleet["target_capacities"]]
                if fleet.get("target_capacities") is not None
                else None
            ),
            fleet_metadata=(
                dict(fleet["metadata"]) if fleet.get("metadata") is not None else None
            ),
            runtime_estimate_seconds=(
                int(runtime_estimate["seconds"])
                if runtime_estimate.get("seconds") is not None
                else None
            ),
            runtime_estimate_source=(
                RuntimeEstimateSource(str(runtime_estimate["source"]))
                if runtime_estimate.get("source") is not None
                else None
            ),
        )

