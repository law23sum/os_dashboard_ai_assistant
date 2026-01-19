"""CLI command to display API session costs."""

from __future__ import annotations

import json
import sys
from typing import List

from assistant_hub.api_session_costs import build_session_costs_snapshot, write_failure_report


def _format_money(value: float) -> str:
    return f"${value:,.4f}"


def _render_table(items: List[dict]) -> None:
    headers = [
        "Provider",
        "Version",
        "Cost / Session (USD)",
        "Credits",
        "Remaining Time (min)",
    ]
    rows = [
        [
            item["provider_label"],
            item["version"],
            _format_money(float(item["cost_per_session_usd"])),
            f"{float(item['credits_remaining']):.0f}",
            f"{int(item['remaining_minutes'])}",
        ]
        for item in items
    ]

    widths = [
        max(len(str(row[idx])) for row in [headers] + rows) if rows else len(headers[idx])
        for idx in range(len(headers))
    ]

    def format_row(row: List[str], align_right: List[bool]) -> str:
        cells = []
        for idx, cell in enumerate(row):
            cell_text = str(cell)
            if align_right[idx]:
                cells.append(cell_text.rjust(widths[idx]))
            else:
                cells.append(cell_text.ljust(widths[idx]))
        return "  ".join(cells)

    align_right = [False, False, True, True, True]
    print(format_row(headers, align_right))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(format_row(row, align_right))


def handle_api_session_costs_command(args, conn) -> int:
    """Handle api-session-costs command."""
    try:
        snapshot = build_session_costs_snapshot(conn)
    except Exception as exc:
        report_path = write_failure_report(f"CLI session cost request failed: {exc}")
        print("Failed to build API session costs.")
        print(f"Report saved to: {report_path}")
        return 1

    if getattr(args, "json", False):
        print(json.dumps(snapshot, indent=2))
        return 0

    items = snapshot.get("items", [])
    if not items:
        error = snapshot.get("error") or "No session cost data available."
        print(error)
        report_path = snapshot.get("report_path")
        if report_path:
            print(f"Report saved to: {report_path}")
        return 1

    _render_table(items)
    print("\nCredits are zero. Remaining time is 0 for all sessions.")
    report_path = snapshot.get("report_path")
    if report_path:
        print(f"\nReport saved to: {report_path}")
    return 0
