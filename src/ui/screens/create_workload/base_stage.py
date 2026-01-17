"""Base stage abstractions for the Create Workload wizard."""

from __future__ import annotations

from enum import IntEnum

from textual.widget import Widget

from src.models.workload_config import WorkloadConfig


class StageId(IntEnum):
    WORKLOAD = 1
    JOB = 2
    HARDWARE = 3


class CreateWorkloadStage(Widget):
    """Base class for a stage UI component."""

    stage_id: StageId
    title: str

    def load_from_config(self, config: WorkloadConfig) -> None:
        """Populate widget controls from an existing config."""

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        """Return an updated config based on current widget state."""
        return config

    def validate(self) -> tuple[bool, str]:
        """Return (ok, message) for gating Next."""
        return True, ""

