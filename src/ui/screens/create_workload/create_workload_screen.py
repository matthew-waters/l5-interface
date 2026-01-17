"""Create Workload wizard screen (Stages 2.1–2.3)."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.binding import Binding

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.stage_1_workload_creation import Stage1WorkloadCreation
from src.ui.screens.create_workload.stage_2_job_specification import Stage2JobSpecification
from src.ui.screens.create_workload.stage_3_hardware_config import Stage3HardwareConfig
from src.ui.widgets.global_widgets.global_header import GlobalHeader


class CreateWorkloadScreen(Screen[None]):
    """Staged workflow for defining and preparing a workload."""
    HEADER_TITLE = "Create Workload"

    DEFAULT_CSS = """
    CreateWorkloadScreen {
        /* The global theme sets Screen overflow-y: auto; for the wizard we want a stable layout. */
        overflow-y: hidden;
        layout: vertical;
    }

    CreateWorkloadScreen #wizard_body {
        height: 1fr;
    }

    CreateWorkloadScreen #drafts_panel {
        width: 1fr;
        padding: 1 1;
    }

    CreateWorkloadScreen #stage_panel {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    /* Ensure tab content has space; TabbedContent defaults to height:auto. */
    CreateWorkloadScreen #stage_tabs {
        height: 1fr;
    }

    CreateWorkloadScreen #stage_tabs > ContentSwitcher {
        height: 1fr;
    }

    CreateWorkloadScreen #stage_tabs TabPane {
        height: 1fr;
        overflow-y: auto;
    }

    /* Modes */
    CreateWorkloadScreen.picking #stage_panel { display: none; }
    CreateWorkloadScreen.editing #drafts_panel { display: none; }

    CreateWorkloadScreen #drafts_table {
        height: 1fr;
    }

    CreateWorkloadScreen #status_line {
        height: 1;
        padding: 0 2;
        color: $text-muted;
    }
    """

    SCREEN_CONTROLS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+n", "new_draft", "New workload"),
        Binding("r", "refresh_drafts", "Refresh drafts"),
        Binding("escape", "exit_to_drafts", "Drafts"),
    ]

    NAVIGATION_CONTROLS = [
    ]        

    BINDINGS = SCREEN_CONTROLS + NAVIGATION_CONTROLS

    def __init__(self) -> None:
        super().__init__()
        self._config: WorkloadConfig | None = None
        self._stage_id: StageId = StageId.WORKLOAD
        self._start_new_draft_on_mount: bool = False
        self._editing: bool = False
        self._status_clear_timer = None

    # --- UI ---
    def compose(self) -> ComposeResult:
        yield GlobalHeader()

        with Horizontal(id="wizard_body"):
            with Vertical(id="drafts_panel"):
                yield Static("Workload drafts", classes="section_title")
                yield DataTable(id="drafts_table", cursor_type="row", zebra_stripes=True)

            with Vertical(id="stage_panel"):
                with TabbedContent(id="stage_tabs", initial="workload"):
                    yield TabPane("2.1 Workload", id="workload")
                    yield TabPane("2.2 Job", id="job")
                    yield TabPane("2.3 Hardware", id="hardware")

        yield Static("", id="status_line")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self._refresh_drafts_list()
        self._set_mode(editing=False)
        if self._start_new_draft_on_mount:
            self._start_new_draft_on_mount = False
            self._new_draft()
        self._focus_drafts_table()

    # Public helpers (used by app/nav to start the flow)
    def start_new_draft(self) -> None:
        # The app/nav may call this immediately after switching screens; guard against
        # being invoked before the screen is mounted (query_one would fail).
        if not self.is_mounted:
            self._start_new_draft_on_mount = True
            return
        self._new_draft()

    # --- Actions / events ---
    def action_go_home(self) -> None:
        self.app.switch_screen("home")

    def action_new_draft(self) -> None:
        self._new_draft()

    def action_save(self) -> None:
        self._save_current()

    def action_refresh_drafts(self) -> None:
        self._refresh_drafts_list()

    def action_exit_to_drafts(self) -> None:
        self._exit_to_drafts()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Conditionally enable/hide actions based on focus.

        Returning False means the action is disabled and not shown in the Footer.
        """
        if action in {"save", "new_draft", "refresh_drafts"}:
            # Only show "new workload" + "refresh drafts" on the drafts list.
            if action in {"new_draft", "refresh_drafts"} and self._editing:
                return False

            focused = getattr(self.app, "focused", None)
            if isinstance(focused, (Input, TextArea)):
                # While typing, treat the input as modal: hide/disable screen bindings
                # to match the Credentials screen behavior (Footer shows none).
                return False
            return True

        if action == "exit_to_drafts":
            # Always allow leaving the editor back to the drafts table.
            return True

        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "new_draft":
                self._new_draft()
            case "refresh_drafts":
                self._refresh_drafts_list()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Selection happens on Enter (action_select_cursor) when cursor_type="row".
        config_id = event.row_key.value
        if config_id:
            self._load_draft(config_id)

    # --- Data helpers ---
    @property
    def _repo(self):
        return getattr(self.app, "storage").workload_drafts

    def _focus_drafts_table(self) -> None:
        try:
            self.query_one("#drafts_table", DataTable).focus()
        except Exception:
            pass

    @staticmethod
    def _fmt_dt_local(dt: datetime | None) -> str:
        if dt is None:
            return "-"
        try:
            return dt.astimezone().strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(dt)

    def _refresh_drafts_list(self) -> None:
        table = self.query_one("#drafts_table", DataTable)
        table.clear(columns=True)
        table.add_columns(
            "Name",
            "Last updated",
            "Interruptible",
            "Delay tolerance",
            "Fleet",
            "Runtime",
        )
        try:
            drafts = self._repo.list_drafts()
        except Exception as e:
            table.add_row(f"Error: {e}", "", "", "", "", "")
            return

        if not drafts:
            table.add_row("No drafts yet.", "", "", "", "", "")
            return

        for d in drafts:
            name = d.name.strip() or "(unnamed)"
            interruptible = (
                "-" if d.interruptible is None else ("Yes" if d.interruptible else "No")
            )
            delay = d.delay_tolerance.label() if d.delay_tolerance is not None else "-"
            fleet = d.fleet_name or (str(d.fleet_id) if d.fleet_id is not None else "-")
            runtime = (
                f"{int(d.runtime_estimate_seconds // 60)} min"
                if d.runtime_estimate_seconds is not None
                else "-"
            )
            table.add_row(
                name,
                self._fmt_dt_local(d.updated_at),
                interruptible,
                delay,
                fleet,
                runtime,
                key=d.config_id,
            )

    def _new_draft(self) -> None:
        self._set_mode(editing=True)
        self._config = self._repo.create_draft()
        self._stage_id = StageId.WORKLOAD
        self._refresh_drafts_list()
        self._set_active_tab(StageId.WORKLOAD)
        self._ensure_stage_mounted(StageId.WORKLOAD)
        self._set_footer_status("Created new draft.")

    def _load_draft(self, config_id: str) -> None:
        cfg = self._repo.get_draft(config_id)
        if cfg is None:
            self._set_footer_status("Unable to load draft.")
            return
        self._set_mode(editing=True)
        self._config = cfg
        self._stage_id = StageId.WORKLOAD
        self._set_active_tab(StageId.WORKLOAD)
        self._ensure_stage_mounted(StageId.WORKLOAD)
        self._set_footer_status("Loaded draft.")

    def _save_current(self) -> None:
        if self._config is None:
            self._set_footer_status("Create or select a draft first.")
            return

        stage = self._active_stage()
        if stage is not None:
            self._config = stage.apply_to_config(self._config)
            self._config = self._config.touch()

        self._repo.save_draft(self._config)
        self._refresh_drafts_list()
        self._set_footer_status("Saved.")

    def _exit_to_drafts(self) -> None:
        """Return to the drafts table view."""
        if not self._editing:
            return
        self._save_current()
        self._set_mode(editing=False)
        self._set_footer_status("Pick a draft or create a new one.")
        self._focus_drafts_table()

    def _clear_status_line(self) -> None:
        try:
            self.query_one("#status_line", Static).update("")
        except Exception:
            pass

    def _set_footer_status(self, text: str, *, auto_clear_seconds: float | None = 3.0) -> None:
        try:
            self.query_one("#status_line", Static).update(text)
        except Exception:
            pass

        # Cancel any previous auto-clear timer.
        if self._status_clear_timer is not None:
            try:
                self._status_clear_timer.stop()
            except Exception:
                pass
            self._status_clear_timer = None

        if not text or auto_clear_seconds is None:
            return

        # Clear after a short delay so status messages don't linger indefinitely.
        self._status_clear_timer = self.set_timer(auto_clear_seconds, self._clear_status_line)

    # --- Stage orchestration ---
    def _active_stage(self) -> CreateWorkloadStage | None:
        # Find the stage widget inside the currently active TabPane.
        tabbed = self.query_one("#stage_tabs", TabbedContent)
        pane = tabbed.active_pane
        if pane is None:
            return None
        for child in pane.children:
            if isinstance(child, CreateWorkloadStage):
                return child
        return None

    def _set_mode(self, *, editing: bool) -> None:
        self._editing = editing
        if editing:
            self.remove_class("picking")
            self.add_class("editing")
        else:
            self.remove_class("editing")
            self.add_class("picking")

    def _stage_id_to_pane_id(self, stage_id: StageId) -> str:
        return {
            StageId.WORKLOAD: "workload",
            StageId.JOB: "job",
            StageId.HARDWARE: "hardware",
        }[stage_id]

    def _pane_id_to_stage_id(self, pane_id: str) -> StageId:
        return {
            "workload": StageId.WORKLOAD,
            "job": StageId.JOB,
            "hardware": StageId.HARDWARE,
        }[pane_id]

    def _set_active_tab(self, stage_id: StageId) -> None:
        tabbed = self.query_one("#stage_tabs", TabbedContent)
        tabbed.active = self._stage_id_to_pane_id(stage_id)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        # Keep stage_id in sync and lazily mount stage widget content.
        pane_id = event.pane.id or ""
        if not pane_id:
            return
        stage_id = self._pane_id_to_stage_id(pane_id)
        self._stage_id = stage_id
        self._ensure_stage_mounted(stage_id)

    def _ensure_stage_mounted(self, stage_id: StageId) -> None:
        if not self._editing:
            return
        tabbed = self.query_one("#stage_tabs", TabbedContent)
        pane = tabbed.query_one(f"#{self._stage_id_to_pane_id(stage_id)}", TabPane)
        for child in pane.children:
            if isinstance(child, CreateWorkloadStage):
                # Already mounted; ensure it is refreshed from current config.
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