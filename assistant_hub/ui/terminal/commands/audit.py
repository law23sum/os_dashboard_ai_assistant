"""Audit ledger CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from assistant_hub.audit import cli as audit_cli


def _parse_payload(raw: str | None) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON payload: {exc}") from exc


def handle_audit_command(args) -> int:
    sub = args.subcommand
    if sub == "emit":
        payload = _parse_payload(args.payload)
        result = audit_cli.emit_event(
            event_type=args.event_type,
            message=args.message,
            payload=payload,
        )
        print(json.dumps(result, indent=2))
        return 0
    if sub == "verify-ledger":
        report = audit_cli.verify_ledger(from_seq=args.from_seq, to_seq=args.to_seq)
        print(json.dumps(report, indent=2))
        return 0
    if sub == "rotate":
        result = audit_cli.rotate_archive_now()
        print(json.dumps(result, indent=2))
        return 0
    if sub == "list-archives":
        archives = audit_cli.list_archives()
        print(json.dumps(archives, indent=2))
        return 0
    if sub == "verify-archive":
        report = audit_cli.verify_archive(Path(args.path))
        print(json.dumps(report, indent=2))
        return 0
    if sub == "restore-archive":
        report = audit_cli.restore_archive(Path(args.path), Path(args.output_dir))
        print(json.dumps(report, indent=2))
        return 0
    print(f"Unknown audit subcommand: {sub}")
    return 1
