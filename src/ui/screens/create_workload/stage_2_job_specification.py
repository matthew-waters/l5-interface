"""Create workload: Stage 2.2 - job configuration (partial for now)."""

from __future__ import annotations

from dataclasses import replace

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Checkbox, Select, Static

from src.models.workload_config import DelayTolerance, WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage2JobSpecification(CreateWorkloadStage):
    stage_id = StageId.JOB_SPEC
    title = "Create Workload -> Job Specification"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_2_CONTAINER_ID):
            with Vertical():
                yield Checkbox("Interruptible (checkpointing supported)", id="interruptible")
                yield Static("Delay tolerance", classes="muted")
                yield Select(
                    # Textual Select expects (label, value). We want the UI to show the plain-English
                    # label, but store the stable enum value in the config JSON.
                    options=[(dt.label(), dt.value) for dt in DelayTolerance],
                    id="delay_tolerance",
                    prompt="Choose delay tolerance…",
                )

    def load_from_config(self, config: WorkloadConfig) -> None:
        interruptible = bool(config.interruptible) if config.interruptible is not None else False
        self.query_one("#interruptible", Checkbox).value = interruptible

        sel = self.query_one("#delay_tolerance", Select)
        if config.delay_tolerance is None:
            sel.clear()
        else:
            sel.value = config.delay_tolerance.value

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        interruptible = self.query_one("#interruptible", Checkbox).value
        delay_raw = self.query_one("#delay_tolerance", Select).value
        if delay_raw is None or delay_raw == Select.BLANK:
            delay = None
        else:
            delay = DelayTolerance(str(delay_raw))
        return replace(config, interruptible=bool(interruptible), delay_tolerance=delay)

    def validate(self) -> tuple[bool, str]:
        delay_raw = self.query_one("#delay_tolerance", Select).value
        if delay_raw is None or delay_raw == Select.BLANK:
            return False, "Please choose a delay tolerance."
        return True, ""

