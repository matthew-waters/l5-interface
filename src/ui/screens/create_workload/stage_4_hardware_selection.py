"""Create workload: Stage 4 - hardware selection."""

from __future__ import annotations

from dataclasses import replace

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Select, Static

from src.backend.data.availability_data import get_available_fleets
from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids


class Stage4HardwareSelection(CreateWorkloadStage):
    stage_id = StageId.HARDWARE_SELECT
    title = "Create Workload -> Hardware Selection"

    CSS_PATH = "./create_workload.tcss"

    REGION_LABELS: dict[str, str] = {
        "eu-west-2": "London",
        "us-west-1": "N. California",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pending_region: str | None = None

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_4_CONTAINER_ID):
            with Vertical():
                with Container(classes="region_select_box") as region_box:
                    region_box.border_title = "Region selection"
                    yield Static("Region", classes="muted")
                    yield Select(options=[], id="region_select", prompt="Loading regions…")

    def on_mount(self) -> None:
        self._load_regions()

    def load_from_config(self, config: WorkloadConfig) -> None:
        sel = self.query_one("#region_select", Select)
        if config.region is None:
            sel.clear()
            self._pending_region = None
            return

        self._pending_region = config.region
        try:
            sel.value = config.region
            self._pending_region = None
        except Exception:
            # Options may not be loaded yet; defer until _set_region_options.
            return

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        region_raw = self.query_one("#region_select", Select).value
        region = (
            str(region_raw)
            if region_raw not in (None, "", Select.BLANK)
            else None
        )
        return replace(config, region=region)

    def validate(self) -> tuple[bool, str]:
        region_raw = self.query_one("#region_select", Select).value
        if not region_raw:
            return False, "Please select a region."
        return True, ""

    @work(thread=True, exclusive=True)
    def _load_regions(self) -> None:
        try:
            fleets = get_available_fleets()
            regions = sorted({fleet.region for fleet in fleets if fleet.region})
            options = [(self._format_region_label(region), region) for region in regions]
            self.app.call_from_thread(self._set_region_options, options)
        except Exception as e:
            self.app.call_from_thread(self._set_region_error, str(e))

    def _set_region_options(self, options: list[tuple[str, str]]) -> None:
        sel = self.query_one("#region_select", Select)
        sel.set_options(options)
        sel.prompt = "Choose region…"

        if self._pending_region:
            valid_regions = {value for _, value in options}
            if self._pending_region in valid_regions:
                sel.value = self._pending_region
            self._pending_region = None

    def _set_region_error(self, message: str) -> None:
        sel = self.query_one("#region_select", Select)
        sel.set_options([])
        sel.prompt = "Unable to load regions"
        notify = getattr(self.app, "notify", None)
        if callable(notify):
            notify(f"Unable to load regions: {message}", severity="error")

    def _format_region_label(self, region: str) -> str:
        label = self.REGION_LABELS.get(region)
        return f"{region} / {label}" if label else region

