"""Create workload: Stage 2.3 - hardware configuration + runtime estimate."""

from __future__ import annotations

from dataclasses import replace

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Select, Static

from src.backend.data.availability_data import get_available_fleets, get_fleet_details
from src.models.workload_config import RuntimeEstimateSource, WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId


class Stage3HardwareConfig(CreateWorkloadStage):
    stage_id = StageId.HARDWARE
    title = "2.3 Hardware Configuration"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._fleet_details = None
        self._fleet_name_by_id: dict[str, str] = {}
        self._pending_fleet_id: str | None = None

    def compose(self) -> ComposeResult:
        with Container(classes="card"):
            yield Static("Spot Fleet selection", classes="section_title")
            with Vertical():
                yield Static("Fleet", classes="muted")
                yield Select(options=[], id="fleet_select", prompt="Loading fleets…")
                yield Static("", id="fleet_status", classes="muted")

                yield Static("Fleet metadata", classes="section_title")
                yield Static("Region: -", id="fleet_region", classes="muted")
                yield Static("Instance types: -", id="fleet_instances", classes="muted")
                yield Static("Target capacities: -", id="fleet_caps", classes="muted")
                yield Static("Purpose: -", id="fleet_purpose", classes="muted")

        with Container(classes="card"):
            yield Static("Runtime estimate (required)", classes="section_title")
            yield Static(
                "Provide an estimate for the selected fleet. Profiling is coming soon; manual entry works now.",
                classes="muted",
            )
            with Horizontal():
                yield Input(id="runtime_minutes", placeholder="Minutes", restrict=r"\d*")
                yield Static("min", classes="muted")
                yield Button("Run profiling (coming soon)", id="run_profiling", variant="default")

    def on_mount(self) -> None:
        self._load_fleets()

    def load_from_config(self, config: WorkloadConfig) -> None:
        self.query_one("#runtime_minutes", Input).value = (
            str(int(config.runtime_estimate_seconds // 60))
            if config.runtime_estimate_seconds is not None
            else ""
        )

        sel = self.query_one("#fleet_select", Select)
        if config.fleet_id is None:
            # Textual Select doesn't allow setting value to None; use clear().
            sel.clear()
            self._pending_fleet_id = None
            self._render_fleet_metadata(None)
            return

        # If options aren't loaded yet, setting .value may be illegal; defer until _set_fleet_options.
        self._pending_fleet_id = str(config.fleet_id)
        if sel.options:
            sel.value = self._pending_fleet_id
            self._pending_fleet_id = None
            # Try to hydrate metadata if the stage is opened later.
            self._load_fleet_details(str(config.fleet_id))
        else:
            self.query_one("#fleet_status", Static).update("Loading fleets…")

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        fleet_raw = self.query_one("#fleet_select", Select).value
        runtime_minutes_raw = self.query_one("#runtime_minutes", Input).value.strip()

        # Textual Select uses a sentinel for "no selection" (Select.BLANK / NoSelection).
        fleet_id = (
            int(fleet_raw)
            if fleet_raw not in (None, "", Select.BLANK)
            else None
        )
        runtime_seconds = int(runtime_minutes_raw) * 60 if runtime_minutes_raw else None

        fleet = self._fleet_details
        fleet_name = self._fleet_name_by_id.get(str(fleet_id)) if fleet_id is not None else None
        return replace(
            config,
            fleet_id=fleet_id,
            fleet_name=(fleet.name if fleet is not None else fleet_name),
            fleet_region=(fleet.region if fleet is not None else None),
            fleet_instance_types=(fleet.instance_types if fleet is not None else None),
            fleet_target_capacities=(fleet.target_capacities if fleet is not None else None),
            fleet_metadata=(fleet.metadata if fleet is not None else None),
            runtime_estimate_seconds=runtime_seconds,
            runtime_estimate_source=(
                RuntimeEstimateSource.MANUAL if runtime_seconds is not None else None
            ),
        )

    def validate(self) -> tuple[bool, str]:
        fleet_raw = self.query_one("#fleet_select", Select).value
        if not fleet_raw:
            return False, "Please select a Spot Fleet."
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

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "fleet_select":
            value = event.value
            if value:
                self._fleet_details = None
                self.query_one("#fleet_status", Static).update("Loading fleet metadata…")
                self._load_fleet_details(str(value))
            else:
                self._render_fleet_metadata(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run_profiling":
            notify = getattr(self.app, "notify", None)
            if callable(notify):
                notify("Profiling is not implemented yet. Please enter a manual runtime.", severity="warning")

    @work(thread=True, exclusive=True)
    def _load_fleets(self) -> None:
        try:
            fleets = get_available_fleets()
            options = [(str(f.id), f.name) for f in fleets]
            self.app.call_from_thread(self._set_fleet_options, options)
        except Exception as e:
            self.app.call_from_thread(self._set_fleet_error, str(e))

    def _set_fleet_options(self, options: list[tuple[str, str]]) -> None:
        self._fleet_name_by_id = {value: label for value, label in options}
        sel = self.query_one("#fleet_select", Select)
        sel.set_options(options)
        sel.prompt = "Choose fleet…"
        self.query_one("#fleet_status", Static).update(
            "Select a fleet to view metadata and placement scores."
        )

        # If we were asked to load a saved fleet before options were available, apply it now.
        if self._pending_fleet_id is not None:
            try:
                sel.value = self._pending_fleet_id
                fleet_id = self._pending_fleet_id
                self._pending_fleet_id = None
                self._load_fleet_details(str(fleet_id))
            except Exception:
                # If the saved id isn't present, clear selection gracefully.
                sel.clear()
                self._pending_fleet_id = None
                self._render_fleet_metadata(None)

    def _set_fleet_error(self, message: str) -> None:
        sel = self.query_one("#fleet_select", Select)
        sel.set_options([])
        sel.prompt = "Unable to load fleets"
        self.query_one("#fleet_status", Static).update(f"Error loading fleets: {message}")

    @work(thread=True, exclusive=True)
    def _load_fleet_details(self, fleet_id: str) -> None:
        try:
            fleet = get_fleet_details(fleet_id)
            self.app.call_from_thread(self._render_fleet_metadata, fleet)
        except Exception as e:
            self.app.call_from_thread(self._set_fleet_error, str(e))

    def _render_fleet_metadata(self, fleet) -> None:
        self._fleet_details = fleet
        if fleet is None:
            self.query_one("#fleet_region", Static).update("Region: -")
            self.query_one("#fleet_instances", Static).update("Instance types: -")
            self.query_one("#fleet_caps", Static).update("Target capacities: -")
            self.query_one("#fleet_purpose", Static).update("Purpose: -")
            return

        region = fleet.region or "-"
        instances = ", ".join(fleet.instance_types or []) if fleet.instance_types else "-"
        caps = ", ".join(str(x) for x in (fleet.target_capacities or [])) if fleet.target_capacities else "-"
        purpose = "-"
        if isinstance(fleet.metadata, dict):
            purpose = str(fleet.metadata.get("purpose") or "-")

        self.query_one("#fleet_region", Static).update(f"Region: {region}")
        self.query_one("#fleet_instances", Static).update(f"Instance types: {instances}")
        self.query_one("#fleet_caps", Static).update(f"Target capacities: {caps}")
        self.query_one("#fleet_purpose", Static).update(f"Purpose: {purpose}")

