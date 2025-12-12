#!/usr/bin/env python3
"""Lightweight defensive network/auth watchdog for the terminal dashboard.

This script keeps to read-only telemetry. It surfaces:
  • Recent authentication failures pulled from the macOS unified log
  • Listening services and the owning binaries
  • Suspicious outbound connections (e.g., unexpected local ports to public IPs)

The JSON summary is written to ~/OS_Dashboard_AI_Assistant/logs/network_watch.json
so the terminal dashboard can render it.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import ipaddress

try:
    import psutil
except ImportError as exc:  # pragma: no cover - guidance printed instead
    sys.stderr.write(
        "psutil is required. Install it with: python3 -m pip install psutil\n"
    )
    raise

OPS_ROOT = Path.home() / "OS_Dashboard_AI_Assistant"
LOG_DIR = OPS_ROOT / "logs"
OUTPUT_PATH = LOG_DIR / "network_watch.json"
DEFAULT_ALLOWLIST = {22, 80, 443, 5173, 3000, 8888, 5000}
DEFAULT_PING_TARGETS = ("1.1.1.1", "8.8.8.8")


def _run_log_show(minutes: int = 10) -> str:
    """Pull login/auth failures from macOS unified log."""
    predicate = (
        'eventMessage CONTAINS[c] "Failed login" || '
        'eventMessage CONTAINS[c] "authentication failure" || '
        'eventMessage CONTAINS[c] "Invalid login" || '
        'eventMessage CONTAINS[c] "Failed to authenticate" || '
        'eventMessage CONTAINS[c] "sshd"'
    )
    cmd = [
        "log",
        "show",
        "--last",
        f"{minutes}m",
        "--predicate",
        predicate,
        "--style",
        "syslog",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if result.returncode not in (0, 65):  # log show returns 65 when nothing matches
        return ""
    return result.stdout or ""


def collect_auth_failures(window_minutes: int = 10) -> dict:
    data = _run_log_show(window_minutes)
    lines = [
        line
        for line in data.splitlines()
        if any(
            marker in line.lower()
            for marker in ("failed", "invalid", "denied", "authentication")
        )
    ]
    return {
        "window_minutes": window_minutes,
        "count": len(lines),
        "recent_events": lines[-5:],  # tail
    }


def _process_name(proc: psutil.Process) -> str:
    try:
        return proc.name()
    except Exception:
        return "unknown"


def _exe_path(proc: psutil.Process) -> str:
    try:
        return proc.exe()
    except Exception:
        return "unknown"


def listening_services(allowlist: set[int]) -> List[dict]:
    seen = {}
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return [{"error": "access_denied"}]
    for conn in connections:
        if conn.status != psutil.CONN_LISTEN:
            continue
        laddr = conn.laddr
        if not laddr:
            continue
        port = laddr.port
        key = (conn.pid, port)
        if key in seen:
            continue
        try:
            proc = psutil.Process(conn.pid) if conn.pid else None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc = None
        entry = {
            "port": port,
            "is_allowed": port in allowlist,
            "process": _process_name(proc) if proc else "unknown",
            "exe": _exe_path(proc) if proc else "unknown",
        }
        seen[key] = entry
    return sorted(seen.values(), key=lambda item: item["port"])


def _is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def interface_throughput(sample_seconds: float, interfaces: Optional[Sequence[str]]) -> List[dict]:
    if sample_seconds <= 0:
        sample_seconds = 1.0
    try:
        start = psutil.net_io_counters(pernic=True)
    except Exception:
        return [{"error": "io_counters_unavailable"}]
    time.sleep(sample_seconds)
    try:
        end = psutil.net_io_counters(pernic=True)
    except Exception:
        return [{"error": "io_counters_unavailable"}]
    metrics: List[dict] = []
    iface_filter = set(interfaces) if interfaces else None
    for name, end_stats in end.items():
        if iface_filter and name not in iface_filter:
            continue
        start_stats = start.get(name)
        if not start_stats:
            continue
        tx_bytes = max(end_stats.bytes_sent - start_stats.bytes_sent, 0)
        rx_bytes = max(end_stats.bytes_recv - start_stats.bytes_recv, 0)
        tx_packets = max(end_stats.packets_sent - start_stats.packets_sent, 0)
        rx_packets = max(end_stats.packets_recv - start_stats.packets_recv, 0)
        tx_bps = tx_bytes / sample_seconds
        rx_bps = rx_bytes / sample_seconds
        metrics.append(
            {
                "interface": name,
                "tx_bytes_per_sec": tx_bps,
                "rx_bytes_per_sec": rx_bps,
                "tx_mbps": round(tx_bps * 8 / 1_000_000, 4),
                "rx_mbps": round(rx_bps * 8 / 1_000_000, 4),
                "tx_packets_per_sec": tx_packets / sample_seconds,
                "rx_packets_per_sec": rx_packets / sample_seconds,
            }
        )
    return sorted(metrics, key=lambda item: item["interface"])


def _airport_binary() -> Optional[Path]:
    path = Path(
        "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    )
    return path if path.exists() else None


def wifi_status() -> dict:
    airport = _airport_binary()
    if not airport:
        return {"status": "unsupported"}
    cmd = [str(airport), "-I"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return {"status": "unavailable"}
    info = {}
    for raw_line in result.stdout.splitlines():
        if ":" not in raw_line:
            continue
        key, value = [segment.strip() for segment in raw_line.split(":", 1)]
        if not key:
            continue
        info[key.lower().replace(" ", "_")] = value
    def _int_field(field: str) -> Optional[int]:
        val = info.get(field)
        if val in (None, ""):
            return None
        try:
            return int(val)
        except ValueError:
            return None
    return {
        "status": "ok",
        "ssid": info.get("ssid"),
        "bssid": info.get("bssid"),
        "rssi": _int_field("agrCtlRSSI".lower()),
        "noise": _int_field("agrCtlNoise".lower()),
        "tx_rate_mbps": _int_field("lastTxRate".lower()),
        "channel": info.get("channel"),
        "auth": info.get("op_mode"),
    }


def latency_probes(targets: Sequence[str], count: int = 3, timeout: int = 2) -> List[dict]:
    probes: List[dict] = []
    for host in targets:
        cmd = [
            "ping",
            "-c",
            str(count),
            "-W",
            str(timeout),
            host,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False, timeout=count * (timeout + 1)
            )
        except FileNotFoundError:
            return [{"error": "ping_missing"}]
        except subprocess.TimeoutExpired:
            probes.append({"host": host, "status": "timeout"})
            continue
        summary_match = re.search(r"= (.*?) ms", result.stdout)
        latency = summary_match.group(1) if summary_match else None
        probes.append(
            {
                "host": host,
                "status": "ok" if result.returncode == 0 else "error",
                "latency": latency,
            }
        )
    return probes


def suspicious_connections(allowlist: set[int]) -> List[dict]:
    events: List[dict] = []
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return [{"error": "access_denied"}]
    for conn in connections:
        if conn.status not in (psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT):
            continue
        if not conn.laddr or not conn.raddr:
            continue
        lport = conn.laddr.port
        rip = conn.raddr.ip
        rport = conn.raddr.port
        if lport in allowlist and _is_private_ip(rip):
            continue
        try:
            proc = psutil.Process(conn.pid) if conn.pid else None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc = None
        events.append(
            {
                "local_port": lport,
                "remote": f"{rip}:{rport}",
                "status": conn.status,
                "process": _process_name(proc) if proc else "unknown",
                "exe": _exe_path(proc) if proc else "unknown",
                "is_private_remote": _is_private_ip(rip),
            }
        )
    return events


def build_report(
    window_minutes: int,
    allowlist: set[int],
    sample_seconds: float,
    interfaces: Optional[Sequence[str]],
    ping_targets: Sequence[str],
) -> dict:
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "auth": collect_auth_failures(window_minutes),
        "listening": listening_services(allowlist),
        "suspicious": suspicious_connections(allowlist),
        "interfaces": interface_throughput(sample_seconds, interfaces),
        "wifi": wifi_status(),
        "latency": latency_probes(ping_targets),
    }


def save_report(report: dict, path: Path = OUTPUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect local auth/network telemetry for the dashboard."
    )
    parser.add_argument(
        "--window-minutes",
        type=int,
        default=10,
        help="Time window for auth failure scan (default: 10).",
    )
    parser.add_argument(
        "--allow",
        type=int,
        nargs="*",
        default=sorted(DEFAULT_ALLOWLIST),
        help="Whitelisted local listening ports.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Where to write the JSON summary.",
    )
    parser.add_argument(
        "--interfaces",
        nargs="*",
        default=None,
        help="Specific network interfaces to sample (default: all).",
    )
    parser.add_argument(
        "--sample-seconds",
        type=float,
        default=1.0,
        help="How long to sample interface throughput (default: 1s).",
    )
    parser.add_argument(
        "--ping",
        nargs="*",
        default=list(DEFAULT_PING_TARGETS),
        help="Targets to probe for latency data.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    allowlist = set(args.allow)
    report = build_report(
        args.window_minutes,
        allowlist,
        args.sample_seconds,
        args.interfaces,
        args.ping,
    )
    save_report(report, args.output)
    print(
        f"[network_watch] auth_failures={report['auth']['count']} "
        f"listening={len(report['listening'])} suspicious={len(report['suspicious'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
