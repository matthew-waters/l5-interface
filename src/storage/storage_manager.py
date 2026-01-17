"""Storage coordination."""

from __future__ import annotations

from pathlib import Path

from src.storage.config_store import ConfigStore
from src.storage.local_json_workload_config_repository import LocalJsonWorkloadConfigRepository
from src.storage.workload_store import WorkloadStore


class StorageManager:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config = ConfigStore(self.data_dir / "configs")
        self.workloads = WorkloadStore(self.data_dir / "workloads")
        # Draft configs for the Create Workload wizard (separate from submitted workloads).
        self.workload_drafts = LocalJsonWorkloadConfigRepository(self.data_dir / "workload_drafts")


