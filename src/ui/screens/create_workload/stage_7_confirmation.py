"""Create workload: Stage 7 - confirmation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container

from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage7Confirmation(CreateWorkloadStage):
    stage_id = StageId.CONFIRMATION
    title = "Create Workload -> Confirmation"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        yield Container(id=ids.STAGE_7_CONTAINER_ID)
