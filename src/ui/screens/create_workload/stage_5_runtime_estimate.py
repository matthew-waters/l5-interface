"""Create workload: Stage 5 - runtime estimate."""

from __future__ import annotations

from dataclasses import replace

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Static

from src.models.workload_config import RuntimeEstimateSource, WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage5RuntimeEstimate(CreateWorkloadStage):
    stage_id = StageId.RUNTIME_ESTIMATE
    title = "Create Workload -> Runtime Estimate"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_5_CONTAINER_ID):
            yield Static("Runtime estimate (required)", classes="section_title")
            yield Static(
                "Provide an estimate for the selected fleet. Profiling is coming soon; manual entry works now.",
                classes="muted",
            )
            with Horizontal():
                yield Input(id="runtime_minutes", placeholder="Minutes", restrict=r"\d*")
                yield Static("min", classes="muted")
                yield Button("Run profiling (coming soon)", id="run_profiling", variant="default")

    def load_from_config(self, config: WorkloadConfig) -> None:
        self.query_one("#runtime_minutes", Input).value = (
            str(int(config.runtime_estimate_seconds // 60))
            if config.runtime_estimate_seconds is not None
            else ""
        )

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        runtime_minutes_raw = self.query_one("#runtime_minutes", Input).value.strip()
        runtime_seconds = int(runtime_minutes_raw) * 60 if runtime_minutes_raw else None
        return replace(
            config,
            runtime_estimate_seconds=runtime_seconds,
            runtime_estimate_source=(
                RuntimeEstimateSource.MANUAL if runtime_seconds is not None else None
            ),
        )

    def validate(self) -> tuple[bool, str]:
        runtime_minutes_raw = self.query_one("#runtime_minutes", Input).value.strip()
        if not runtime_minutes_raw:
            return False, "Please enter a runtime estimate (minutes)."
        try:
            minutes = int(runtime_minutes_raw)
            if minutes <= 0:
                return False, "Runtime estimate must be > 0 minutes."
        except Exception:
            return False, "Runtime estimate must be an integer number of minutes."
        return True, ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run_profiling":
            notify = getattr(self.app, "notify", None)
            if callable(notify):
                notify("Profiling is not implemented yet. Please enter a manual runtime.", severity="warning")
