"""Create workload: Stage 6 - scheduling."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container

from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage6Scheduling(CreateWorkloadStage):
    stage_id = StageId.SCHEDULING
    title = "Create Workload -> Scheduling"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        yield Container(id=ids.STAGE_6_CONTAINER_ID)
