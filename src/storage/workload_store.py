"""Workload persistence (JSON files in `data/workloads/`)."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from src.models.workload import Workload, WorkloadStatus


class WorkloadStore:
    def __init__(self, workloads_dir: Path) -> None:
        self.workloads_dir = workloads_dir
        self.workloads_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, workload_id: str) -> Path:
        return self.workloads_dir / f"{workload_id}.json"

    def list(self) -> list[Workload]:
        workloads: list[Workload] = []
        for path in sorted(self.workloads_dir.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                workloads.append(Workload.from_json(data))
            except Exception:
                # If a file is corrupted, skip it for now (surface later via UI).
                continue
        return workloads

    def get(self, workload_id: str) -> Workload | None:
        path = self._path_for(workload_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return Workload.from_json(data)

    def save(self, workload: Workload) -> None:
        path = self._path_for(workload.workload_id)
        with path.open("w", encoding="utf-8") as f:
            json.dump(workload.to_json(), f, indent=2, sort_keys=True)

    def create_draft(self, name: str) -> Workload:
        now = datetime.now(tz=timezone.utc)
        workload = Workload(
            workload_id=str(uuid4()),
            name=name,
            status=WorkloadStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.save(workload)
        return workload

    def update(
        self,
        workload_id: str,
        *,
        name: str | None = None,
        status: WorkloadStatus | None = None,
        scheduled_start: datetime | None = None,
        expected_runtime_seconds: int | None = None,
        expected_carbon_intensity: float | None = None,
        fleet: str | None = None,
        region: str | None = None,
    ) -> Workload | None:
        current = self.get(workload_id)
        if current is None:
            return None
        now = datetime.now(tz=timezone.utc)
        updated = replace(
            current,
            name=name if name is not None else current.name,
            status=status if status is not None else current.status,
            updated_at=now,
            scheduled_start=scheduled_start if scheduled_start is not None else current.scheduled_start,
            expected_runtime_seconds=(
                expected_runtime_seconds
                if expected_runtime_seconds is not None
                else current.expected_runtime_seconds
            ),
            expected_carbon_intensity=(
                expected_carbon_intensity
                if expected_carbon_intensity is not None
                else current.expected_carbon_intensity
            ),
            fleet=fleet if fleet is not None else current.fleet,
            region=region if region is not None else current.region,
        )
        self.save(updated)
        return updated

    def bulk_save(self, workloads: Iterable[Workload]) -> None:
        for w in workloads:
            self.save(w)

