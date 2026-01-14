"""Workload model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self


class WorkloadStatus(StrEnum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHED"
    RUNNING = "RUN"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class Workload:
    """A user-defined workload and its execution planning metadata."""

    workload_id: str
    name: str
    status: WorkloadStatus

    created_at: datetime
    updated_at: datetime

    # Planning/execution metadata (optional until later stages exist)
    scheduled_start: datetime | None = None
    expected_runtime_seconds: int | None = None
    expected_carbon_intensity: float | None = None  # gCO2/kWh

    fleet: str | None = None
    region: str | None = None

    @staticmethod
    def _dt_to_iso(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def _dt_from_iso(value: str) -> datetime:
        return datetime.fromisoformat(value)

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self._dt_to_iso(self.created_at)
        data["updated_at"] = self._dt_to_iso(self.updated_at)
        if self.scheduled_start is not None:
            data["scheduled_start"] = self._dt_to_iso(self.scheduled_start)
        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            workload_id=str(data["workload_id"]),
            name=str(data["name"]),
            status=WorkloadStatus(str(data["status"])),
            created_at=cls._dt_from_iso(str(data["created_at"])),
            updated_at=cls._dt_from_iso(str(data["updated_at"])),
            scheduled_start=(
                cls._dt_from_iso(str(data["scheduled_start"]))
                if data.get("scheduled_start") is not None
                else None
            ),
            expected_runtime_seconds=(
                int(data["expected_runtime_seconds"])
                if data.get("expected_runtime_seconds") is not None
                else None
            ),
            expected_carbon_intensity=(
                float(data["expected_carbon_intensity"])
                if data.get("expected_carbon_intensity") is not None
                else None
            ),
            fleet=str(data["fleet"]) if data.get("fleet") is not None else None,
            region=str(data["region"]) if data.get("region") is not None else None,
        )


