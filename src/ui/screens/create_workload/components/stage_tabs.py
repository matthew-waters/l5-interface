"""Tabbed stage area for CreateWorkloadScreen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids
from src.ui.screens.create_workload.stage_1_general_details import Stage1GeneralDetails
from src.ui.screens.create_workload.stage_2_job_semantics import Stage2JobSemantics
from src.ui.screens.create_workload.stage_3_job_specification import Stage3JobSpecification
from src.ui.screens.create_workload.stage_4_hardware_selection import Stage4HardwareSelection
from src.ui.screens.create_workload.stage_5_runtime_estimate import Stage5RuntimeEstimate
from src.ui.screens.create_workload.stage_6_scheduling import Stage6Scheduling
from src.ui.screens.create_workload.stage_7_confirmation import Stage7Confirmation


class CreateWorkloadStageTabs(Widget):
    """A TabbedContent hosting the create workload stages, lazily mounted."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config: WorkloadConfig | None = None
        self._stage_id: StageId = StageId.GENERAL_DETAILS

    def compose(self) -> ComposeResult:
        with TabbedContent(id=ids.STAGE_TABBED_CONTENT_ID, initial="workload"):
            yield TabPane("1. General Details", id="workload")
            yield TabPane("2. Job Semantics", id="semantics")
            yield TabPane("3. Job Specification", id="job_spec")
            yield TabPane("4. Hardware Select", id="hardware")
            yield TabPane("5. Runtime Estimate", id="runtime")
            yield TabPane("6. Scheduling", id="scheduling")
            yield TabPane("7. Confirmation", id="confirmation")

    def load_config(self, config: WorkloadConfig | None) -> None:
        """Set the active config and refresh the current stage UI from it."""
        self._config = config
        self._ensure_stage_mounted(self._stage_id)

    def active_stage(self) -> CreateWorkloadStage | None:
        tabbed = self.query_one(f"#{ids.STAGE_TABBED_CONTENT_ID}", TabbedContent)
        pane = tabbed.active_pane
        if pane is None:
            return None
        for child in pane.children:
            if isinstance(child, CreateWorkloadStage):
                return child
        return None

    def go_to(self, stage_id: StageId) -> None:
        self._apply_stage_to_config(self._stage_id)
        self._stage_id = stage_id
        tabbed = self.query_one(f"#{ids.STAGE_TABBED_CONTENT_ID}", TabbedContent)
        tabbed.active = self._stage_id_to_pane_id(stage_id)
        self._ensure_stage_mounted(stage_id)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        pane_id = event.pane.id or ""
        if not pane_id:
            return
        previous_stage_id = self._stage_id
        stage_id = self._pane_id_to_stage_id(pane_id)
        if stage_id != previous_stage_id:
            self._apply_stage_to_config(previous_stage_id)
        self._stage_id = stage_id
        self._ensure_stage_mounted(stage_id)

    def _ensure_stage_mounted(self, stage_id: StageId) -> None:
        tabbed = self.query_one(f"#{ids.STAGE_TABBED_CONTENT_ID}", TabbedContent)
        pane = tabbed.query_one(f"#{self._stage_id_to_pane_id(stage_id)}", TabPane)
        for child in pane.children:
            if isinstance(child, CreateWorkloadStage):
                if self._config is not None:
                    child.load_from_config(self._config)
                return

        stage: CreateWorkloadStage
        if stage_id == StageId.GENERAL_DETAILS:
            stage = Stage1GeneralDetails()
        elif stage_id == StageId.JOB_SEMANTICS:
            stage = Stage2JobSemantics()
        elif stage_id == StageId.JOB_SPECIFICATION:
            stage = Stage3JobSpecification()
        elif stage_id == StageId.HARDWARE_SELECT:
            stage = Stage4HardwareSelection()
        elif stage_id == StageId.RUNTIME_ESTIMATE:
            stage = Stage5RuntimeEstimate()
        elif stage_id == StageId.SCHEDULING:
            stage = Stage6Scheduling()
        else:
            stage = Stage7Confirmation()

        pane.mount(stage)
        if self._config is not None:
            stage.load_from_config(self._config)

    def _apply_stage_to_config(self, stage_id: StageId) -> None:
        if self._config is None:
            return
        tabbed = self.query_one(f"#{ids.STAGE_TABBED_CONTENT_ID}", TabbedContent)
        pane = tabbed.query_one(f"#{self._stage_id_to_pane_id(stage_id)}", TabPane)
        for child in pane.children:
            if isinstance(child, CreateWorkloadStage):
                try:
                    self._config = child.apply_to_config(self._config)
                except ValueError as exc:
                    notify = getattr(self.app, "notify", None)
                    if callable(notify):
                        notify(
                            f"Unable to save changes: {exc}",
                            severity="error",
                        )
                return

    @staticmethod
    def _stage_id_to_pane_id(stage_id: StageId) -> str:
        return {
            StageId.GENERAL_DETAILS: "workload",
            StageId.JOB_SEMANTICS: "semantics",
            StageId.JOB_SPECIFICATION: "job_spec",
            StageId.HARDWARE_SELECT: "hardware",
            StageId.RUNTIME_ESTIMATE: "runtime",
            StageId.SCHEDULING: "scheduling",
            StageId.CONFIRMATION: "confirmation",
        }[stage_id]

    @staticmethod
    def _pane_id_to_stage_id(pane_id: str) -> StageId:
        return {
            "workload": StageId.GENERAL_DETAILS,
            "semantics": StageId.JOB_SEMANTICS,
            "job_spec": StageId.JOB_SPECIFICATION,
            "hardware": StageId.HARDWARE_SELECT,
            "runtime": StageId.RUNTIME_ESTIMATE,
            "scheduling": StageId.SCHEDULING,
            "confirmation": StageId.CONFIRMATION,
        }[pane_id]

