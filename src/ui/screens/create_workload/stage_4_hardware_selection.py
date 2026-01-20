"""Create workload: Stage 4 - hardware selection."""

from __future__ import annotations

from dataclasses import replace

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Select, Static

from src.backend.data.availability_data import get_available_fleets
from src.backend.data.fleet.models import RequestGroup
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

    REGION_AZS: dict[str, list[str]] = {
        "eu-west-2": ["euw2-az1", "euw2-az2", "euw2-az3"],
        "us-west-1": ["usw1-az1", "usw1-az3"],
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pending_region: str | None = None
        self._pending_fleet_id: str | None = None
        self._pending_az: str | None = None
        self._pending_target_capacity: int | None = None
        self._fleets: list[RequestGroup] | None = None

    def compose(self) -> ComposeResult:
        with Container(id=ids.STAGE_4_CONTAINER_ID):
            with VerticalScroll():
                with Container(classes="region_select_box") as region_box:
                    region_box.border_title = "Region selection"
                    yield Static("Region", classes="muted")
                    yield Select(options=[], id="region_select", prompt="Loading regions…")
                    yield Static("Availability zone", classes="muted")
                    yield Select(options=[], id="az_select", prompt="Select region first")
                with Container(classes="fleet_select_box") as fleet_box:
                    fleet_box.border_title = "Fleet selection"
                    yield Static("Fleet", classes="muted")
                    yield Select(options=[], id="fleet_select", prompt="Select region first")
                    yield Static("Target capacity", classes="muted")
                    yield Select(options=[], id="target_capacity_select", prompt="Select fleet first")

    def on_mount(self) -> None:
        self._load_regions()

    def load_from_config(self, config: WorkloadConfig) -> None:
        region_select = self.query_one("#region_select", Select)
        fleet_select = self.query_one("#fleet_select", Select)
        if config.region is None:
            region_select.clear()
            self._pending_region = None
            self._pending_fleet_id = None
            self._pending_az = None
            self._pending_target_capacity = None
            self._refresh_fleet_options(None)
            self._refresh_az_options(None)
            self._refresh_target_capacity_options(None)
            return

        self._pending_region = config.region
        self._pending_fleet_id = str(config.fleet_id) if config.fleet_id is not None else None
        self._pending_az = config.availability_zone
        self._pending_target_capacity = config.fleet_target_capacity
        if self._fleets is None:
            self._refresh_fleet_options(None, loading=True)
            self._refresh_az_options(None, loading=True)
            self._refresh_target_capacity_options(None, loading=True)
        try:
            region_select.value = config.region
            self._pending_region = None
        except Exception:
            # Options may not be loaded yet; defer until _set_region_options.
            return
        self._refresh_fleet_options(config.region, preferred_id=self._pending_fleet_id)
        self._refresh_az_options(config.region, preferred_az=self._pending_az)
        self._refresh_target_capacity_options(
            self._pending_fleet_id, preferred_capacity=self._pending_target_capacity
        )
        if self._pending_fleet_id:
            try:
                fleet_select.value = self._pending_fleet_id
                self._pending_fleet_id = None
            except Exception:
                # If options aren't ready, keep pending.
                return
        if self._pending_az:
            try:
                self.query_one("#az_select", Select).value = self._pending_az
                self._pending_az = None
            except Exception:
                return
        if self._pending_target_capacity is not None:
            try:
                self.query_one("#target_capacity_select", Select).value = str(
                    self._pending_target_capacity
                )
                self._pending_target_capacity = None
            except Exception:
                return

    def apply_to_config(self, config: WorkloadConfig) -> WorkloadConfig:
        region_raw = self.query_one("#region_select", Select).value
        region = (
            str(region_raw)
            if region_raw not in (None, "", Select.BLANK)
            else None
        )
        fleet_raw = self.query_one("#fleet_select", Select).value
        fleet_id = (
            int(fleet_raw)
            if fleet_raw not in (None, "", Select.BLANK)
            else None
        )
        target_capacity_raw = self.query_one("#target_capacity_select", Select).value
        target_capacity = (
            int(target_capacity_raw)
            if target_capacity_raw not in (None, "", Select.BLANK)
            else None
        )
        az_raw = self.query_one("#az_select", Select).value
        availability_zone = (
            str(az_raw)
            if az_raw not in (None, "", Select.BLANK)
            else None
        )
        fleet_name = None
        if fleet_id is not None and self._fleets:
            fleet = next((f for f in self._fleets if f.id == fleet_id), None)
            fleet_name = fleet.name if fleet is not None else None
        return replace(
            config,
            region=region,
            availability_zone=availability_zone,
            fleet_id=fleet_id,
            fleet_name=fleet_name,
            fleet_target_capacity=target_capacity,
        )

    def validate(self) -> tuple[bool, str]:
        region_raw = self.query_one("#region_select", Select).value
        if not region_raw:
            return False, "Please select a region."
        fleet_raw = self.query_one("#fleet_select", Select).value
        if not fleet_raw:
            return False, "Please select a fleet."
        target_capacity_raw = self.query_one("#target_capacity_select", Select).value
        if not target_capacity_raw:
            return False, "Please select a target capacity."
        az_raw = self.query_one("#az_select", Select).value
        if not az_raw:
            return False, "Please select an availability zone."
        return True, ""

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "region_select":
            region = str(event.value) if event.value else None
            self._pending_fleet_id = None
            self._pending_az = None
            self._pending_target_capacity = None
            self._refresh_fleet_options(region)
            self._refresh_az_options(region)
            self._refresh_target_capacity_options(None)
        elif event.select.id == "fleet_select":
            fleet_id = str(event.value) if event.value else None
            self._pending_target_capacity = None
            self._refresh_target_capacity_options(fleet_id)

    @work(thread=True, exclusive=True)
    def _load_regions(self) -> None:
        try:
            fleets = get_available_fleets()
            self.app.call_from_thread(self._set_fleets, fleets)
        except Exception as e:
            self.app.call_from_thread(self._set_region_error, str(e))

    def _set_fleets(self, fleets: list[RequestGroup]) -> None:
        self._fleets = fleets
        regions = sorted({fleet.region for fleet in fleets if fleet.region})
        region_options = [(self._format_region_label(region), region) for region in regions]
        region_select = self.query_one("#region_select", Select)
        region_select.set_options(region_options)
        region_select.prompt = "Choose region…"

        if self._pending_region:
            valid_regions = {value for _, value in region_options}
            if self._pending_region in valid_regions:
                region_select.value = self._pending_region
                self._refresh_fleet_options(self._pending_region, preferred_id=self._pending_fleet_id)
                self._refresh_az_options(self._pending_region, preferred_az=self._pending_az)
                self._refresh_target_capacity_options(
                    self._pending_fleet_id,
                    preferred_capacity=self._pending_target_capacity,
                )
            self._pending_region = None
            return

        self._refresh_fleet_options(None)
        self._refresh_az_options(None)
        self._refresh_target_capacity_options(None)

    def _set_region_error(self, message: str) -> None:
        sel = self.query_one("#region_select", Select)
        sel.set_options([])
        sel.prompt = "Unable to load regions"
        self._refresh_fleet_options(None)
        self._refresh_az_options(None)
        self._refresh_target_capacity_options(None)
        notify = getattr(self.app, "notify", None)
        if callable(notify):
            notify(f"Unable to load regions: {message}", severity="error")

    def _format_region_label(self, region: str) -> str:
        label = self.REGION_LABELS.get(region)
        return f"{region} / {label}" if label else region

    def _get_region_azs(self, region: str | None) -> list[str]:
        if not region:
            return []
        return list(self.REGION_AZS.get(region, []))

    def _refresh_fleet_options(
        self,
        region: str | None,
        *,
        preferred_id: str | None = None,
        loading: bool = False,
    ) -> None:
        fleet_select = self.query_one("#fleet_select", Select)
        if loading or self._fleets is None:
            fleet_select.set_options([])
            fleet_select.prompt = "Loading fleets…"
            fleet_select.disabled = True
            return

        if not region:
            fleet_select.set_options([])
            fleet_select.prompt = "Select region first"
            fleet_select.disabled = True
            return

        options = [
            (fleet.name, str(fleet.id))
            for fleet in self._fleets
            if fleet.region == region
        ]
        fleet_select.set_options(options)
        fleet_select.prompt = "Choose fleet…"
        fleet_select.disabled = False
        if preferred_id:
            valid_ids = {value for _, value in options}
            if preferred_id in valid_ids:
                fleet_select.value = preferred_id
        if not preferred_id:
            self._refresh_target_capacity_options(None)

    def _refresh_az_options(
        self,
        region: str | None,
        *,
        preferred_az: str | None = None,
        loading: bool = False,
    ) -> None:
        az_select = self.query_one("#az_select", Select)
        if loading:
            az_select.set_options([])
            az_select.prompt = "Loading zones…"
            az_select.disabled = True
            return

        azs = self._get_region_azs(region)
        if not azs:
            az_select.set_options([])
            az_select.prompt = "Select region first"
            az_select.disabled = True
            return

        options = [(az, az) for az in azs]
        az_select.set_options(options)
        az_select.prompt = "Choose availability zone…"
        az_select.disabled = False
        if preferred_az and preferred_az in azs:
            az_select.value = preferred_az

    def _refresh_target_capacity_options(
        self,
        fleet_id: str | None,
        *,
        preferred_capacity: int | None = None,
        loading: bool = False,
    ) -> None:
        select = self.query_one("#target_capacity_select", Select)
        if loading:
            select.set_options([])
            select.prompt = "Loading capacities…"
            select.disabled = True
            return

        if not fleet_id or self._fleets is None:
            select.set_options([])
            select.prompt = "Select fleet first"
            select.disabled = True
            return

        fleet = next((f for f in self._fleets if str(f.id) == str(fleet_id)), None)
        capacities = fleet.target_capacities if fleet is not None else None
        if not capacities:
            select.set_options([])
            select.prompt = "No capacities available"
            select.disabled = True
            return

        options = [(str(cap), str(cap)) for cap in capacities]
        select.set_options(options)
        select.prompt = "Choose capacity…"
        select.disabled = False
        if preferred_capacity is not None:
            value = str(preferred_capacity)
            valid = {v for _, v in options}
            if value in valid:
                select.value = value

