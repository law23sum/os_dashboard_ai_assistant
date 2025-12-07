"""Temporary GUI entry that proxies to CLI."""
from assistant_hub.ui.terminal.cli import main


def launch() -> None:
    main()
