"""Navigation/actions bar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static


class NavigationBar(Static):
    """Bottom navigation hints."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Keys: [h] home  [w] workloads  [t] timeline  [e] execution  [c] create (home)  [q] quit",
            classes="muted",
        )

