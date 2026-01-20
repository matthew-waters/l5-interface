"""Create workload: Stage 2 - job semantics (partial for now)."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Input, Static, Switch

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage2JobSemantics(CreateWorkloadStage):
    stage_id = StageId.JOB_SEMANTICS
    title = "Create Workload -> Job Semantics"

    CSS_PATH = "./create_workload.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_2_CONTAINER_ID):
            with VerticalScroll():
                with Container(classes="runtime_bounds_box") as runtime_bounds:
                    runtime_bounds.border_title = "Runtime Bounds"
                    with Vertical(classes="runtime_input"):
                        yield Static("Deadline", classes="section_title")
                        yield Static(
                            "Set a hard deadline for when the job must finish (optional).",
                            classes="muted",
                        )
                        with Horizontal(classes="runtime_input_fields"):
                            yield Switch("Enable deadline", id="deadline_enabled")
                            yield Input(id="deadline_at", placeholder="YYYY-MM-DD HH:MM")

                    with Vertical(classes="runtime_input"):
                        yield Static("Earliest start time", classes="section_title")
                        yield Static(
                            "Restrict scheduling so the job cannot start before this time (optional).",
                            classes="muted",
                        )
                        with Horizontal(classes="runtime_input_fields"):
                            yield Switch("Enable earliest start", id="earliest_start_enabled")
                            yield Input(id="earliest_start_at", placeholder="YYYY-MM-DD HH:MM")

    def load_from_config(self, config: WorkloadConfig) -> None:
        deadline_input = self.query_one("#deadline_at", Input)
        deadline_enabled = self.query_one("#deadline_enabled", Switch)
        self._set_deadline_error(False)
        if config.deadline_at is None:
            deadline_enabled.value = False
            deadline_input.value = ""
        else:
            deadline_enabled.value = True
            deadline_input.value = self._format_dt(config.deadline_at)
        self._set_deadline_enabled(deadline_enabled.value)

        earliest_input = self.query_one("#earliest_start_at", Input)
        earliest_enabled = self.query_one("#earliest_start_enabled", Switch)
        self._set_earliest_start_error(False)
        if config.earliest_start_at is None:
            earliest_enabled.value = False
            earliest_input.value = ""
        else:
            earliest_enabled.value = True
            earliest_input.value = self._format_dt(config.earliest_start_at)
        self._set_earliest_start_enabled(earliest_enabled.value)

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        deadline_enabled = self.query_one("#deadline_enabled", Switch).value
        deadline_raw = self.query_one("#deadline_at", Input).value.strip()
        if not deadline_enabled or not deadline_raw:
            deadline_at = None
            self._set_deadline_error(False)
        else:
            try:
                deadline_at = self._parse_dt(deadline_raw)
                self._set_deadline_error(False)
            except ValueError:
                self._set_deadline_error(True)
                deadline_at = config.deadline_at

        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_raw = self.query_one("#earliest_start_at", Input).value.strip()
        if not earliest_enabled or not earliest_raw:
            earliest_start_at = None
            self._set_earliest_start_error(False)
        else:
            try:
                earliest_start_at = self._parse_dt(earliest_raw)
                self._set_earliest_start_error(False)
            except ValueError:
                self._set_earliest_start_error(True)
                earliest_start_at = config.earliest_start_at

        return replace(
            config,
            deadline_at=deadline_at,
            earliest_start_at=earliest_start_at,
        )

    def validate(self) -> tuple[bool, str]:
        deadline_enabled = self.query_one("#deadline_enabled", Switch).value
        deadline_raw = self.query_one("#deadline_at", Input).value.strip()
        if deadline_enabled and deadline_raw:
            try:
                self._parse_dt(deadline_raw)
            except ValueError:
                return False, "Deadline must be in YYYY-MM-DD HH:MM format."
        if deadline_enabled and not deadline_raw:
            return False, "Enter a deadline or disable the toggle."

        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_raw = self.query_one("#earliest_start_at", Input).value.strip()
        if earliest_enabled and not earliest_raw:
            return False, "Enter an earliest start time or disable the toggle."
        if earliest_enabled and earliest_raw:
            try:
                self._parse_dt(earliest_raw)
            except ValueError:
                return False, "Earliest start must be in YYYY-MM-DD HH:MM format."
        return True, ""

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "deadline_enabled":
            self._set_deadline_enabled(event.switch.value)
            self._validate_deadline_input()
        elif event.switch.id == "earliest_start_enabled":
            self._set_earliest_start_enabled(event.switch.value)
            self._validate_earliest_start_input()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "deadline_at":
            self._validate_deadline_input()
        elif event.input.id == "earliest_start_at":
            self._validate_earliest_start_input()

    def _set_deadline_enabled(self, enabled: bool) -> None:
        deadline_input = self.query_one("#deadline_at", Input)
        deadline_input.disabled = not enabled
        if not enabled:
            deadline_input.value = ""
            self._set_deadline_error(False)

    def _set_earliest_start_enabled(self, enabled: bool) -> None:
        earliest_input = self.query_one("#earliest_start_at", Input)
        earliest_input.disabled = not enabled
        if not enabled:
            earliest_input.value = ""
            self._set_earliest_start_error(False)

    def _validate_deadline_input(self) -> None:
        deadline_enabled = self.query_one("#deadline_enabled", Switch).value
        deadline_raw = self.query_one("#deadline_at", Input).value.strip()
        if not deadline_enabled or not deadline_raw:
            self._set_deadline_error(False)
            return
        try:
            self._parse_dt(deadline_raw)
            self._set_deadline_error(False)
        except ValueError:
            self._set_deadline_error(True)

    def _validate_earliest_start_input(self) -> None:
        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_raw = self.query_one("#earliest_start_at", Input).value.strip()
        if not earliest_enabled or not earliest_raw:
            self._set_earliest_start_error(False)
            return
        try:
            self._parse_dt(earliest_raw)
            self._set_earliest_start_error(False)
        except ValueError:
            self._set_earliest_start_error(True)

    def _set_deadline_error(self, has_error: bool) -> None:
        input_widget = self.query_one("#deadline_at", Input)
        if has_error:
            input_widget.add_class("input_error")
        else:
            input_widget.remove_class("input_error")

    def _set_earliest_start_error(self, has_error: bool) -> None:
        input_widget = self.query_one("#earliest_start_at", Input)
        if has_error:
            input_widget.add_class("input_error")
        else:
            input_widget.remove_class("input_error")

    @staticmethod
    def _parse_dt(value: str) -> datetime:
        raw = value.replace(" ", "T")
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise ValueError("Invalid date/time. Use YYYY-MM-DD HH:MM") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _format_dt(value: datetime) -> str:
        dt = value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M")

