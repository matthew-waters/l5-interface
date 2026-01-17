"""Storage-agnostic repository interface for draft workload configs."""

from __future__ import annotations

from typing import Protocol

from src.models.workload_config import WorkloadConfig


class WorkloadConfigRepository(Protocol):
    """Repository for draft `WorkloadConfig` objects."""

    def list_drafts(self) -> list[WorkloadConfig]:
        """List draft configs (ordering is repository-defined)."""

    def get_draft(self, config_id: str) -> WorkloadConfig | None:
        """Get a draft config by id."""

    def create_draft(self) -> WorkloadConfig:
        """Create and persist a new draft config with an id."""

    def save_draft(self, config: WorkloadConfig) -> None:
        """Persist the draft config."""

    def delete_draft(self, config_id: str) -> bool:
        """Delete the draft config (returns True if deleted)."""

