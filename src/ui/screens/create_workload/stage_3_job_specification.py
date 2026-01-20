"""Create workload: Stage 3 - job specification (placeholder)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container

from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage3JobSpecification(CreateWorkloadStage):
    stage_id = StageId.JOB_SPECIFICATION
    title = "Create Workload -> Job Specification"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        yield Container(id=ids.STAGE_3_CONTAINER_ID)
