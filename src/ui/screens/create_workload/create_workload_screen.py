"""Create Workload wizard screen (Stages 2.1–2.3)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, ListItem, ListView, Static

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.base_stage import CreateWorkloadStage, StageId
from src.ui.screens.create_workload.stage_1_workload_creation import Stage1WorkloadCreation
from src.ui.screens.create_workload.stage_2_job_specification import Stage2JobSpecification
from src.ui.screens.create_workload.stage_3_hardware_config import Stage3HardwareConfig
from src.ui.widgets.header.global_header import GlobalHeader


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

    /* Draft picker mode: list takes full width; hide stage editor. */
    CreateWorkloadScreen.picking #drafts_panel {
        width: 1fr;
        min-width: 28;
    }

    CreateWorkloadScreen.picking #stage_panel {
        display: none;
    }

    /* Editing mode: show split layout. */
    CreateWorkloadScreen.editing #drafts_panel {
        display: none;
    }

    CreateWorkloadScreen.editing #stage_panel {
        display: block;
        width: 1fr;
    }

    CreateWorkloadScreen #drafts_panel {
        width: 40;
        min-width: 28;
        border: solid $panel;
        padding: 1 1;
    }

    CreateWorkloadScreen #stage_panel {
        width: 1fr;
        border: solid $panel;
        padding: 1 2;
    }

    CreateWorkloadScreen #wizard_footer {
        /* Textual CSS doesn't consistently support `height: auto` for containers. */
        height: 4;
        border-top: solid $panel;
        padding: 0 2;
        align: left middle;
    }

    CreateWorkloadScreen #stage_stepper {
        width: 1fr;
        align: center middle;
    }

    CreateWorkloadScreen #stage_stepper .step {
        padding: 0 1;
        color: $text-muted;
    }

    CreateWorkloadScreen #stage_stepper .step.current {
        text-style: bold;
        color: $text;
    }
    """

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+n", "new_draft", "New draft"),
        ("left", "back", "Back"),
        ("right", "next", "Next"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._config: WorkloadConfig | None = None
        self._stage_id: StageId = StageId.WORKLOAD
        self._start_new_draft_on_mount: bool = False
        self._editing: bool = False

    # --- UI ---
    def compose(self) -> ComposeResult:
        yield GlobalHeader()

        with Horizontal(id="wizard_body"):
            with Vertical(id="drafts_panel"):
                yield Static("Resume draft", classes="section_title")
                yield Static("Select a saved draft or create a new one.", classes="muted")
                yield ListView(id="drafts_list")
                with Horizontal():
                    yield Button("New draft", id="new_draft", variant="primary")
                    yield Button("Refresh", id="refresh_drafts", variant="default")

            with Vertical(id="stage_panel"):
                yield Static("", id="stage_title", classes="section_title")
                yield Container(id="stage_container")

        with Horizontal(id="wizard_footer"):
            yield Button("Back", id="back_btn")
            yield Button("Save", id="save_btn", variant="primary")
            yield Button("Next", id="next_btn", variant="default")
            with Horizontal(id="stage_stepper"):
                yield Static("2.1 Workload", id="step_workload", classes="step")
                yield Static(">", classes="muted")
                yield Static("2.2 Job", id="step_job", classes="step")
                yield Static(">", classes="muted")
                yield Static("2.3 Hardware", id="step_hardware", classes="step")
            yield Static("", id="footer_status", classes="muted")

    def on_mount(self) -> None:
        self._refresh_drafts_list()
        self._set_mode(editing=False)
        if self._start_new_draft_on_mount:
            self._start_new_draft_on_mount = False
            self._new_draft()

        # Focus the drafts list for quick keyboard selection.
        try:
            self.query_one("#drafts_list", ListView).focus()
        except Exception:
            pass

    # Public helpers (used by app/nav to start the flow)
    def start_new_draft(self) -> None:
        # The app/nav may call this immediately after switching screens; guard against
        # being invoked before the screen is mounted (query_one would fail).
        if not self.is_mounted:
            self._start_new_draft_on_mount = True
            return
        self._new_draft()

    # --- Actions / events ---
    def action_new_draft(self) -> None:
        self._new_draft()

    def action_save(self) -> None:
        self._save_current()

    def action_back(self) -> None:
        self._go_back()

    def action_next(self) -> None:
        self._go_next()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "new_draft":
                self._new_draft()
            case "refresh_drafts":
                self._refresh_drafts_list()
            case "save_btn":
                self._save_current()
            case "back_btn":
                self._go_back()
            case "next_btn":
                self._go_next()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, DraftListItem):
            self._load_draft(item.config_id)

    # --- Data helpers ---
    @property
    def _repo(self):
        return getattr(self.app, "storage").workload_drafts

    def _refresh_drafts_list(self) -> None:
        lv = self.query_one("#drafts_list", ListView)
        # Clear existing rows. (We avoid per-row widget IDs to sidestep DuplicateIds errors.)
        if hasattr(lv, "clear") and callable(getattr(lv, "clear")):
            lv.clear()  # type: ignore[attr-defined]
        else:
            lv.remove_children()
        try:
            drafts = self._repo.list_drafts()
        except Exception as e:
            lv.append(ListItem(Static(f"Error: {e}", classes="muted")))
            return

        if not drafts:
            lv.append(ListItem(Static("No drafts yet.", classes="muted")))
            return

        for d in drafts:
            name = d.name.strip() or "(unnamed)"
            lv.append(DraftListItem(config_id=d.config_id, label=name))

    def _new_draft(self) -> None:
        self._set_mode(editing=True)
        self._config = self._repo.create_draft()
        self._stage_id = StageId.WORKLOAD
        self._refresh_drafts_list()
        self._render_stage()
        self._update_stepper()
        self._set_footer_status("Created new draft.")

    def _load_draft(self, config_id: str) -> None:
        cfg = self._repo.get_draft(config_id)
        if cfg is None:
            self._set_footer_status("Unable to load draft.")
            return
        self._set_mode(editing=True)
        self._config = cfg
        self._stage_id = StageId.WORKLOAD
        self._render_stage()
        self._update_stepper()
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

    def _go_back(self) -> None:
        if not self._editing:
            return
        if self._stage_id == StageId.WORKLOAD:
            # Return to draft picker (without forcing the config panel to show).
            self._save_current()
            self._set_mode(editing=False)
            self._update_stepper()
            self._set_footer_status("Pick a draft or create a new one.")
            return
        self._stage_id = StageId(self._stage_id - 1)
        self._render_stage()
        self._update_stepper()

    def _go_next(self) -> None:
        if not self._editing:
            self._set_footer_status("Select a draft or create a new one first.")
            return
        if self._config is None:
            self._set_footer_status("Create or select a draft first.")
            return

        stage = self._active_stage()
        if stage is None:
            return

        ok, msg = stage.validate()
        if not ok:
            notify = getattr(self.app, "notify", None)
            if callable(notify):
                notify(msg, severity="warning")
            self._set_footer_status(msg)
            return

        # Apply changes and persist before advancing.
        self._save_current()

        if self._stage_id == StageId.HARDWARE:
            self._set_footer_status("Stage 2.3 complete (scheduling comes next).")
            return

        self._stage_id = StageId(self._stage_id + 1)
        self._render_stage()
        self._update_stepper()

    def _set_footer_status(self, text: str) -> None:
        self.query_one("#footer_status", Static).update(text)

    # --- Stage orchestration ---
    def _active_stage(self) -> CreateWorkloadStage | None:
        container = self.query_one("#stage_container", Container)
        for child in container.children:
            if isinstance(child, CreateWorkloadStage):
                return child
        return None

    def _render_stage(self) -> None:
        if not self._editing:
            return
        title = self.query_one("#stage_title", Static)
        container = self.query_one("#stage_container", Container)
        container.remove_children()

        stage: CreateWorkloadStage
        if self._stage_id == StageId.WORKLOAD:
            stage = Stage1WorkloadCreation()
        elif self._stage_id == StageId.JOB:
            stage = Stage2JobSpecification()
        else:
            stage = Stage3HardwareConfig()

        title.update(stage.title)
        container.mount(stage)
        if self._config is not None:
            stage.load_from_config(self._config)

    def _set_mode(self, *, editing: bool) -> None:
        self._editing = editing
        if editing:
            self.remove_class("picking")
            self.add_class("editing")
        else:
            self.remove_class("editing")
            self.add_class("picking")

        # Update footer buttons to match mode.
        self.query_one("#back_btn", Button).disabled = not editing
        self.query_one("#save_btn", Button).disabled = not editing
        self.query_one("#next_btn", Button).disabled = not editing
        self._update_stepper()

    def _update_stepper(self) -> None:
        if not self._editing:
            # Stepper is a container; just remove the current highlight.
            for wid in ("#step_workload", "#step_job", "#step_hardware"):
                try:
                    self.query_one(wid, Static).remove_class("current")
                except Exception:
                    pass
            return

        step_map = {
            StageId.WORKLOAD: "#step_workload",
            StageId.JOB: "#step_job",
            StageId.HARDWARE: "#step_hardware",
        }
        for sid, selector in step_map.items():
            w = self.query_one(selector, Static)
            if sid == self._stage_id:
                w.add_class("current")
            else:
                w.remove_class("current")


class DraftListItem(ListItem):
    """List item representing a draft workload config."""

    def __init__(self, *, config_id: str, label: str) -> None:
        super().__init__(Static(label, classes="muted"))
        self.config_id = config_id