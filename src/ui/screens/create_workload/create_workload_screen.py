"""Create Workload wizard screen (Stages 1–7)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, Static, TextArea
from textual.binding import Binding

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import StageId
from src.ui.screens.create_workload.components import AutoClearStatus, CreateWorkloadStageTabs, DraftsTable
from src.ui.screens.create_workload.components import ids
from src.ui.widgets.global_widgets.global_header import GlobalHeader


class CreateWorkloadScreen(Screen[None]):
    """Staged workflow for defining and preparing a workload."""
    HEADER_TITLE = "Create Workload"

    CSS_PATH = "./create_workload.tcss"

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+n", "new_draft", "New workload"),
        Binding("r", "refresh_drafts", "Refresh drafts"),
        Binding("escape", "exit_to_drafts", "Drafts"),
        Binding("delete", "delete_draft", "Delete draft"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._config: WorkloadConfig | None = None
        self._stage_id: StageId = StageId.GENERAL_DETAILS
        self._start_new_draft_on_mount: bool = False
        self._editing: bool = False

    # --- UI ---
    def compose(self) -> ComposeResult:
        yield GlobalHeader()

        with Horizontal(id=ids.WIZARD_BODY_ID):
            with Vertical(id=ids.DRAFTS_PANEL_ID):
                yield Static("Workload drafts", classes="section_title")
                yield DraftsTable(id=ids.DRAFTS_TABLE_WIDGET_ID)

            with Vertical(id=ids.STAGE_PANEL_ID):
                yield CreateWorkloadStageTabs(id=ids.STAGE_TABS_WIDGET_ID)

        yield AutoClearStatus("", id=ids.STATUS_LINE_ID)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self._refresh_drafts_list()
        self._set_mode(editing=False)
        if self._start_new_draft_on_mount:
            self._start_new_draft_on_mount = False
            self._new_draft()
        self._drafts_table().focus_table()

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

    def action_delete_draft(self) -> None:
        # Only meaningful on the drafts list view.
        if self._editing:
            return

        config_id = self._drafts_table().selected_config_id()
        if not config_id:
            self._set_footer_status("Select a draft row first.")
            return

        ok = False
        try:
            ok = bool(self._repo.delete_draft(str(config_id)))
        except Exception as e:
            self._set_footer_status(f"Unable to delete draft: {e}")
            return

        if ok:
            self._set_footer_status("Draft deleted.")
        else:
            self._set_footer_status("Unable to delete draft.")
        self._refresh_drafts_list()
        self._drafts_table().focus_table()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Conditionally enable/hide actions based on focus.

        Returning False means the action is disabled and not shown in the Footer.
        """
        if action in {"save", "new_draft", "refresh_drafts", "delete_draft"}:
            # Only show "new workload" + "refresh drafts" on the drafts list.
            if action in {"new_draft", "refresh_drafts", "delete_draft"} and self._editing:
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

    def on_drafts_table_draft_selected(self, event: DraftsTable.DraftSelected) -> None:
        self._load_draft(event.config_id)

    # --- Data helpers ---
    @property
    def _repo(self):
        return getattr(self.app, "storage").workload_drafts

    def _drafts_table(self) -> DraftsTable:
        return self.query_one(f"#{ids.DRAFTS_TABLE_WIDGET_ID}", DraftsTable)

    def _stage_tabs(self) -> CreateWorkloadStageTabs:
        return self.query_one(f"#{ids.STAGE_TABS_WIDGET_ID}", CreateWorkloadStageTabs)

    def _status(self) -> AutoClearStatus:
        return self.query_one(f"#{ids.STATUS_LINE_ID}", AutoClearStatus)

    def _refresh_drafts_list(self) -> None:
        try:
            drafts = self._repo.list_drafts()
        except Exception as e:
            self._drafts_table().show_error(str(e))
            return
        self._drafts_table().set_drafts(drafts)

    def _new_draft(self) -> None:
        self._set_mode(editing=True)
        self._config = self._repo.create_draft()
        self._stage_id = StageId.GENERAL_DETAILS
        self._refresh_drafts_list()
        self._stage_tabs().go_to(StageId.GENERAL_DETAILS)
        self._stage_tabs().load_config(self._config)
        self._set_footer_status("Created new draft.")

    def _load_draft(self, config_id: str) -> None:
        cfg = self._repo.get_draft(config_id)
        if cfg is None:
            self._set_footer_status("Unable to load draft.")
            return
        self._set_mode(editing=True)
        self._config = cfg
        self._stage_id = StageId.GENERAL_DETAILS
        self._stage_tabs().go_to(StageId.GENERAL_DETAILS)
        self._stage_tabs().load_config(self._config)
        self._set_footer_status("Loaded draft.")

    def _save_current(self) -> None:
        if self._config is None:
            self._set_footer_status("Create or select a draft first.")
            return

        stage = self._stage_tabs().active_stage()
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
        self._drafts_table().focus_table()

    def _set_footer_status(self, text: str, *, auto_clear_seconds: float | None = 3.0) -> None:
        self._status().set_status(text, auto_clear_seconds=auto_clear_seconds)

    def _set_mode(self, *, editing: bool) -> None:
        self._editing = editing
        if editing:
            self.remove_class("picking")
            self.add_class("editing")
        else:
            self.remove_class("editing")
            self.add_class("picking")

    # Stage orchestration is handled by CreateWorkloadStageTabs.