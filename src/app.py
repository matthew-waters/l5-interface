"""Main application entry point."""

from __future__ import annotations

from src.ui.app import L5InterfaceApp


def main() -> None:
    """CLI entrypoint."""
    L5InterfaceApp().run()


if __name__ == "__main__":
    main()

