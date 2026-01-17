"""Local JSON storage for draft workload configs (files under `data/workload_drafts/`)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.models.workload_config import WorkloadConfig


class LocalJsonWorkloadConfigRepository:
    """Store draft `WorkloadConfig` objects as JSON files."""

    def __init__(self, drafts_dir: Path) -> None:
        self.drafts_dir = drafts_dir
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, config_id: str) -> Path:
        return self.drafts_dir / f"{config_id}.json"

    def list_drafts(self) -> list[WorkloadConfig]:
        drafts: list[WorkloadConfig] = []
        for path in sorted(self.drafts_dir.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                drafts.append(WorkloadConfig.from_json(data))
            except Exception:
                continue
        # newest first (more useful for “resume”)
        return sorted(drafts, key=lambda d: d.updated_at, reverse=True)

    def get_draft(self, config_id: str) -> WorkloadConfig | None:
        path = self._path_for(config_id)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return WorkloadConfig.from_json(data)
        except Exception:
            return None

    def create_draft(self) -> WorkloadConfig:
        now = datetime.now(tz=timezone.utc)
        config = WorkloadConfig(
            version=1,
            config_id=str(uuid4()),
            created_at=now,
            updated_at=now,
        )
        self.save_draft(config)
        return config

    def save_draft(self, config: WorkloadConfig) -> None:
        path = self._path_for(config.config_id)
        with path.open("w", encoding="utf-8") as f:
            json.dump(config.to_json(), f, indent=2, sort_keys=True)

    def delete_draft(self, config_id: str) -> bool:
        path = self._path_for(config_id)
        try:
            path.unlink(missing_ok=True)
            return True
        except Exception:
            return False

