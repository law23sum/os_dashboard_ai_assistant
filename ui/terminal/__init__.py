"""Terminal/CLI interface for OS Dashboard."""

__all__ = ["main", "create_cli_parser"]


def main() -> int:
    from .cli import main as _main

    return _main()


def create_cli_parser():
    from .cli import create_cli_parser as _create

    return _create()
