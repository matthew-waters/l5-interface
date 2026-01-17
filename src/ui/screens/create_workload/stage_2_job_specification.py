"""Create workload: Stage 2.2 - job configuration (partial for now)."""

from __future__ import annotations

from dataclasses import replace

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Checkbox, Select, Static

from src.models.workload_config import DelayTolerance, WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId


class Stage2JobSpecification(CreateWorkloadStage):
    stage_id = StageId.JOB
    title = "2.2 Job Specification"

    def compose(self) -> ComposeResult:
        with Container(classes="card"):
            yield Static("Job configuration", classes="section_title")
            with Vertical():
                yield Static(
                    "We only capture high-level scheduling-relevant options here for now.",
                    classes="muted",
                )
                yield Checkbox("Interruptible (checkpointing supported)", id="interruptible")
                yield Static("Delay tolerance", classes="muted")
                yield Select(
                    options=[(dt.value, dt.label()) for dt in DelayTolerance],
                    id="delay_tolerance",
                    prompt="Choose delay tolerance…",
                )

    def load_from_config(self, config: WorkloadConfig) -> None:
        interruptible = bool(config.interruptible) if config.interruptible is not None else False
        self.query_one("#interruptible", Checkbox).value = interruptible

        sel = self.query_one("#delay_tolerance", Select)
        sel.value = config.delay_tolerance.value if config.delay_tolerance is not None else None

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        interruptible = self.query_one("#interruptible", Checkbox).value
        delay_raw = self.query_one("#delay_tolerance", Select).value
        delay = DelayTolerance(str(delay_raw)) if delay_raw else None
        return replace(config, interruptible=bool(interruptible), delay_tolerance=delay)

    def validate(self) -> tuple[bool, str]:
        delay_raw = self.query_one("#delay_tolerance", Select).value
        if not delay_raw:
            return False, "Please choose a delay tolerance."
        return True, ""

