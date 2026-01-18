"""Create workload: Stage 2.1 - workload definition."""

from __future__ import annotations

from dataclasses import replace

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, Static, TextArea

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage1WorkloadCreation(CreateWorkloadStage):
    stage_id = StageId.WORKLOAD
    title = "2.1 Workload Creation"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_1_CONTAINER_ID):
            with Vertical():
                yield Static("Name", classes="muted")
                yield Input(id="name", placeholder="e.g. Train model v2")
                yield Static("Description", classes="muted")
                yield TextArea(id="description")

    def load_from_config(self, config: WorkloadConfig) -> None:
        self.query_one("#name", Input).value = config.name or ""
        self.query_one("#description", TextArea).text = config.description or ""

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        name = self.query_one("#name", Input).value.strip()
        desc = self.query_one("#description", TextArea).text.strip()
        return replace(config, name=name, description=desc)

    def validate(self) -> tuple[bool, str]:
        name = self.query_one("#name", Input).value.strip()
        if not name:
            return False, "Please enter a workload name."
        return True, ""

