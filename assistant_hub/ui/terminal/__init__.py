"""Terminal/CLI interface for AI OS Console."""

__all__ = ["main", "create_cli_parser"]


def __getattr__(name):
    if name in __all__:
        from .cli import main, create_cli_parser

        return main if name == "main" else create_cli_parser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + __all__)
