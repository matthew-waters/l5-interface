"""Tabbed stage area for CreateWorkloadScreen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.components import ids
from src.ui.screens.create_workload.stage_1_workload_creation import Stage1WorkloadCreation
from src.ui.screens.create_workload.stage_2_job_specification import Stage2JobSpecification
from src.ui.screens.create_workload.stage_3_hardware_config import Stage3HardwareConfig


class CreateWorkloadStageTabs(Widget):
    """A TabbedContent hosting the create workload stages, lazily mounted."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config: WorkloadConfig | None = None
        self._stage_id: StageId = StageId.WORKLOAD

    def compose(self) -> ComposeResult:
        with TabbedContent(id=ids.STAGE_TABBED_CONTENT_ID, initial="workload"):
            yield TabPane("2.1 Workload", id="workload")
            yield TabPane("2.2 Job", id="job")
            yield TabPane("2.3 Hardware", id="hardware")

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
        self._stage_id = stage_id
        tabbed = self.query_one(f"#{ids.STAGE_TABBED_CONTENT_ID}", TabbedContent)
        tabbed.active = self._stage_id_to_pane_id(stage_id)
        self._ensure_stage_mounted(stage_id)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        pane_id = event.pane.id or ""
        if not pane_id:
            return
        stage_id = self._pane_id_to_stage_id(pane_id)
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
        if stage_id == StageId.WORKLOAD:
            stage = Stage1WorkloadCreation()
        elif stage_id == StageId.JOB:
            stage = Stage2JobSpecification()
        else:
            stage = Stage3HardwareConfig()

        pane.mount(stage)
        if self._config is not None:
            stage.load_from_config(self._config)

    @staticmethod
    def _stage_id_to_pane_id(stage_id: StageId) -> str:
        return {
            StageId.WORKLOAD: "workload",
            StageId.JOB: "job",
            StageId.HARDWARE: "hardware",
        }[stage_id]

    @staticmethod
    def _pane_id_to_stage_id(pane_id: str) -> StageId:
        return {
            "workload": StageId.WORKLOAD,
            "job": StageId.JOB,
            "hardware": StageId.HARDWARE,
        }[pane_id]

