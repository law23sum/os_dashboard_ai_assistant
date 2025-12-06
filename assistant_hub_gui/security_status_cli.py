#!/usr/bin/env python3
"""CLI helper to read/write the cyber defense status consumed by the Assistant Hub dashboard."""
from __future__ import annotations

import argparse
from datetime import datetime
from typing import Dict

from assistant_hub.db import (
    SecurityStatus,
    SECURITY_STATUS_CHOICES,
    init_db,
    load_security_status,
    save_security_status,
)

DEFAULT_MESSAGES: Dict[str, str] = {
    "secure": "mac_guard supervisor online. No active threats detected.",
    "vulnerable": "mac_guard detected a degraded posture. Review guard health.",
    "exploited": "mac_guard isolated the host after a critical alert.",
    "offline": "mac_guard is offline. Start the supervisor to resume monitoring.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update or inspect the cyber defense status for the dashboard.")
    parser.add_argument(
        "status",
        choices=SECURITY_STATUS_CHOICES,
        help="Threat posture to record.",
    )
    parser.add_argument(
        "--message",
        help="Optional message shown on the dashboard. Defaults to a stock message for the chosen status.",
    )
    parser.add_argument(
        "--source",
        default="mac_guard",
        help="Component writing the status (used for auditing only).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress human-readable output; useful for scripting.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print the existing status before applying any updates.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conn = init_db()
    try:
        if args.show and not args.quiet:
            current = load_security_status(conn)
            print(
                f"Current status: {current.status} | message='{current.message}' | "
                f"updated_at={current.updated_at or 'n/a'} | source={current.source}"
            )

        message = args.message or DEFAULT_MESSAGES.get(args.status, "Status updated via CLI.")
        updated_at = datetime.now().isoformat(timespec="seconds")
        payload = SecurityStatus(
            status=args.status,
            message=message,
            updated_at=updated_at,
            source=args.source,
        )
        save_security_status(conn, payload)

        if not args.quiet:
            print(
                f"Recorded status='{payload.status}' message='{payload.message}' "
                f"(source={payload.source}, updated_at={payload.updated_at})"
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
