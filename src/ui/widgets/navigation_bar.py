"""Navigation/actions bar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class NavigationBar(Static):
    """Bottom navigation hints."""

    DEFAULT_CSS = """
    NavigationBar {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold](h)[/bold] home  [bold](w)[/bold] workloads  [bold](t)[/bold] timeline  [bold](e)[/bold] execution  [bold](c)[/bold] create  [bold](r)[/bold] credentials  [bold](q)[/bold] quit",
            classes="muted",
        )

