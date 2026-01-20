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
                            yield Input(id="deadline_date", placeholder="YYYY-MM-DD")
                            yield Input(id="deadline_time", placeholder="HH:MM")

                    with Vertical(classes="runtime_input"):
                        yield Static("Earliest start time", classes="section_title")
                        yield Static(
                            "Restrict scheduling so the job cannot start before this time (optional).",
                            classes="muted",
                        )
                        with Horizontal(classes="runtime_input_fields"):
                            yield Switch("Enable earliest start", id="earliest_start_enabled")
                            yield Input(id="earliest_start_date", placeholder="YYYY-MM-DD")
                            yield Input(id="earliest_start_time", placeholder="HH:MM")

    def load_from_config(self, config: WorkloadConfig) -> None:
        deadline_date = self.query_one("#deadline_date", Input)
        deadline_time = self.query_one("#deadline_time", Input)
        deadline_enabled = self.query_one("#deadline_enabled", Switch)
        self._set_deadline_error(False)
        if config.deadline_at is None:
            deadline_enabled.value = False
            deadline_date.value = ""
            deadline_time.value = ""
        else:
            deadline_enabled.value = True
            deadline_date.value = self._format_date(config.deadline_at)
            deadline_time.value = self._format_time(config.deadline_at)
        self._set_deadline_enabled(deadline_enabled.value)

        earliest_date = self.query_one("#earliest_start_date", Input)
        earliest_time = self.query_one("#earliest_start_time", Input)
        earliest_enabled = self.query_one("#earliest_start_enabled", Switch)
        self._set_earliest_start_error(False)
        if config.earliest_start_at is None:
            earliest_enabled.value = False
            earliest_date.value = ""
            earliest_time.value = ""
        else:
            earliest_enabled.value = True
            earliest_date.value = self._format_date(config.earliest_start_at)
            earliest_time.value = self._format_time(config.earliest_start_at)
        self._set_earliest_start_enabled(earliest_enabled.value)

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        deadline_enabled = self.query_one("#deadline_enabled", Switch).value
        deadline_date = self.query_one("#deadline_date", Input).value.strip()
        deadline_time = self.query_one("#deadline_time", Input).value.strip()
        if not deadline_enabled or not deadline_date or not deadline_time:
            deadline_at = None
            self._set_deadline_error(False)
        else:
            try:
                deadline_at = self._parse_dt_parts(deadline_date, deadline_time)
                self._set_deadline_error(False)
            except ValueError:
                self._set_deadline_error(True)
                deadline_at = config.deadline_at

        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_date = self.query_one("#earliest_start_date", Input).value.strip()
        earliest_time = self.query_one("#earliest_start_time", Input).value.strip()
        if not earliest_enabled or not earliest_date or not earliest_time:
            earliest_start_at = None
            self._set_earliest_start_error(False)
        else:
            try:
                earliest_start_at = self._parse_dt_parts(earliest_date, earliest_time)
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
        deadline_date = self.query_one("#deadline_date", Input).value.strip()
        deadline_time = self.query_one("#deadline_time", Input).value.strip()
        if deadline_enabled and deadline_date and deadline_time:
            try:
                self._parse_dt_parts(deadline_date, deadline_time)
            except ValueError:
                return False, "Deadline must be in YYYY-MM-DD and HH:MM format."
        if deadline_enabled and (not deadline_date or not deadline_time):
            return False, "Enter a deadline date and time or disable the toggle."

        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_date = self.query_one("#earliest_start_date", Input).value.strip()
        earliest_time = self.query_one("#earliest_start_time", Input).value.strip()
        if earliest_enabled and (not earliest_date or not earliest_time):
            return False, "Enter an earliest start date and time or disable the toggle."
        if earliest_enabled and earliest_date and earliest_time:
            try:
                self._parse_dt_parts(earliest_date, earliest_time)
            except ValueError:
                return False, "Earliest start must be in YYYY-MM-DD and HH:MM format."
        return True, ""

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "deadline_enabled":
            self._set_deadline_enabled(event.switch.value)
            self._validate_deadline_input()
        elif event.switch.id == "earliest_start_enabled":
            self._set_earliest_start_enabled(event.switch.value)
            self._validate_earliest_start_input()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in {"deadline_date", "deadline_time"}:
            self._validate_deadline_input()
        elif event.input.id in {"earliest_start_date", "earliest_start_time"}:
            self._validate_earliest_start_input()

    def _set_deadline_enabled(self, enabled: bool) -> None:
        deadline_date = self.query_one("#deadline_date", Input)
        deadline_time = self.query_one("#deadline_time", Input)
        deadline_date.disabled = not enabled
        deadline_time.disabled = not enabled
        if not enabled:
            deadline_date.value = ""
            deadline_time.value = ""
            self._set_deadline_error(False)

    def _set_earliest_start_enabled(self, enabled: bool) -> None:
        earliest_date = self.query_one("#earliest_start_date", Input)
        earliest_time = self.query_one("#earliest_start_time", Input)
        earliest_date.disabled = not enabled
        earliest_time.disabled = not enabled
        if not enabled:
            earliest_date.value = ""
            earliest_time.value = ""
            self._set_earliest_start_error(False)

    def _validate_deadline_input(self) -> None:
        deadline_enabled = self.query_one("#deadline_enabled", Switch).value
        deadline_date = self.query_one("#deadline_date", Input).value.strip()
        deadline_time = self.query_one("#deadline_time", Input).value.strip()
        if not deadline_enabled or not deadline_date or not deadline_time:
            self._set_deadline_error(False)
            return
        try:
            self._parse_dt_parts(deadline_date, deadline_time)
            self._set_deadline_error(False)
        except ValueError:
            self._set_deadline_error(True)

    def _validate_earliest_start_input(self) -> None:
        earliest_enabled = self.query_one("#earliest_start_enabled", Switch).value
        earliest_date = self.query_one("#earliest_start_date", Input).value.strip()
        earliest_time = self.query_one("#earliest_start_time", Input).value.strip()
        if not earliest_enabled or not earliest_date or not earliest_time:
            self._set_earliest_start_error(False)
            return
        try:
            self._parse_dt_parts(earliest_date, earliest_time)
            self._set_earliest_start_error(False)
        except ValueError:
            self._set_earliest_start_error(True)

    def _set_deadline_error(self, has_error: bool) -> None:
        date_input = self.query_one("#deadline_date", Input)
        time_input = self.query_one("#deadline_time", Input)
        if has_error:
            date_input.add_class("input_error")
            time_input.add_class("input_error")
        else:
            date_input.remove_class("input_error")
            time_input.remove_class("input_error")

    def _set_earliest_start_error(self, has_error: bool) -> None:
        date_input = self.query_one("#earliest_start_date", Input)
        time_input = self.query_one("#earliest_start_time", Input)
        if has_error:
            date_input.add_class("input_error")
            time_input.add_class("input_error")
        else:
            date_input.remove_class("input_error")
            time_input.remove_class("input_error")

    @staticmethod
    def _parse_dt_parts(date_value: str, time_value: str) -> datetime:
        raw = f"{date_value}T{time_value}"
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise ValueError("Invalid date/time. Use YYYY-MM-DD and HH:MM") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _format_date(value: datetime) -> str:
        dt = value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def _format_time(value: datetime) -> str:
        dt = value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.strftime("%H:%M")

