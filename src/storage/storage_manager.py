"""Storage coordination."""

from __future__ import annotations

from pathlib import Path

from src.storage.workload_store import WorkloadStore


class StorageManager:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.workloads = WorkloadStore(self.data_dir / "workloads")


