"""Command-line utility to inspect the OS Dashboard canonical specification."""
from __future__ import annotations

import argparse
import json
from typing import Any

from . import spec_summary, architecture_summary, planes_summary


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(description="OS Dashboard Spec Explorer")
    parser.add_argument(
        "section",
        nargs="?",
        default="mission",
        choices=["mission", "architecture", "planes", "failure", "all"],
        help="Which section to display",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Render output as text or JSON",
    )
    args = parser.parse_args(argv)

    data = {}
    if args.section in ("mission", "all"):
        data["mission"] = spec_summary()
    if args.section in ("architecture", "all"):
        data["architecture"] = architecture_summary()
    if args.section in ("planes", "all"):
        data["planes"] = planes_summary()
    if args.section in ("failure", "all"):
        from . import failure_summary

        data["failure"] = failure_summary()

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        for section, payload in data.items():
            print(section.upper())
            print("=" * len(section))
            if isinstance(payload, dict):
                for key, value in payload.items():
                    print(f"{key}:")
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            print(f"  {subkey}:")
                            for item in subvalue:
                                print(f"    - {item}")
                    else:
                        for item in value:
                            print(f"  - {item}")
            else:
                print(payload)
            print()

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
