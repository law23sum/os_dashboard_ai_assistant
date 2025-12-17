"""Network Monitoring API router - provides network device monitoring and security alerts."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# Path to network watch script and logs
OPS_ROOT = Path.home() / "OS_Dashboard_AI_Assistant"
LOG_DIR = OPS_ROOT / "logs"
NETWORK_WATCH_JSON = LOG_DIR / "network_watch.json"
NETWORK_WATCH_SCRIPT = Path(__file__).parent.parent.parent / "ops_root_assets" / "scripts" / "network_watch.py"
KNOWN_DEVICES_FILE = LOG_DIR / "known_devices.json"

# Suspicious hostname patterns (exported for config endpoint)
SUSPICIOUS_HOSTNAME_PATTERNS = [
    r"vps\d+",
    r"server\d+",
    r"0onevps",
    r"cloud\d+",
    r"aws-",
    r"gcp-",
    r"azure-",
    r"\.local\.",
]


def _load_known_devices() -> Dict[str, Any]:
    """Load known devices from file."""
    if not KNOWN_DEVICES_FILE.exists():
        return {"hostnames": [], "mac_addresses": [], "ips": [], "blocked_devices": []}
    try:
        with open(KNOWN_DEVICES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"hostnames": [], "mac_addresses": [], "ips": [], "blocked_devices": []}


def _save_known_devices(devices: Dict[str, Any]) -> None:
    """Save known devices to file."""
    KNOWN_DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(KNOWN_DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)


class NetworkDevice(BaseModel):
    """Network device information."""
    
    ip: str
    mac: str
    hostname: Optional[str] = None
    interface: str
    is_suspicious: bool = False
    suspicious_reasons: List[str] = Field(default_factory=list)
    is_known: bool = False


class NetworkInterface(BaseModel):
    """Network interface statistics."""
    
    interface: str
    tx_bytes_per_sec: float
    rx_bytes_per_sec: float
    tx_mbps: float
    rx_mbps: float
    tx_packets_per_sec: float
    rx_packets_per_sec: float


class AuthFailure(BaseModel):
    """Authentication failure information."""
    
    window_minutes: int
    count: int
    recent_events: List[str] = Field(default_factory=list)


class ListeningService(BaseModel):
    """Listening network service."""
    
    port: int
    is_allowed: bool
    process: str
    exe: str


class SuspiciousConnection(BaseModel):
    """Suspicious network connection."""
    
    local_port: int
    remote: str
    status: str
    process: str
    exe: str
    is_private_remote: bool


class WiFiStatus(BaseModel):
    """WiFi connection status."""
    
    status: str
    ssid: Optional[str] = None
    bssid: Optional[str] = None
    rssi: Optional[int] = None
    noise: Optional[int] = None
    tx_rate_mbps: Optional[int] = None
    channel: Optional[str] = None
    auth: Optional[str] = None


class LatencyProbe(BaseModel):
    """Network latency probe result."""
    
    host: str
    status: str
    latency: Optional[str] = None


class NetworkMonitoringReport(BaseModel):
    """Complete network monitoring report."""
    
    generated_at: str
    auth: AuthFailure
    listening: List[ListeningService]
    suspicious: List[SuspiciousConnection]
    devices: List[NetworkDevice]
    suspicious_devices: List[NetworkDevice]
    suspicious_device_count: int
    interfaces: List[NetworkInterface]
    wifi: WiFiStatus
    latency: List[LatencyProbe]


def _load_network_report() -> Optional[Dict[str, Any]]:
    """Load network watch JSON report if it exists."""
    if not NETWORK_WATCH_JSON.exists():
        return None
    
    try:
        with open(NETWORK_WATCH_JSON, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading network report: {e}", file=sys.stderr)
        return None


def _run_network_watch_script() -> bool:
    """Run the network watch script to generate fresh data."""
    if not NETWORK_WATCH_SCRIPT.exists():
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(NETWORK_WATCH_SCRIPT), "--window-minutes", "10"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error running network watch script: {e}", file=sys.stderr)
        return False


@router.get("/status", response_model=NetworkMonitoringReport)
async def get_network_status(refresh: bool = False) -> NetworkMonitoringReport:
    """
    Get network monitoring status and device list.
    
    Args:
        refresh: If True, run network watch script to generate fresh data before returning.
    
    Returns:
        Network monitoring report with devices, connections, and security status.
    """
    if refresh:
        _run_network_watch_script()
    
    data = _load_network_report()
    
    if not data:
        # Return empty/default report if no data available
        return NetworkMonitoringReport(
            generated_at=datetime.utcnow().isoformat() + "Z",
            auth=AuthFailure(window_minutes=10, count=0),
            listening=[],
            suspicious=[],
            devices=[],
            suspicious_devices=[],
            suspicious_device_count=0,
            interfaces=[],
            wifi=WiFiStatus(status="unavailable"),
            latency=[],
        )
    
    # Convert devices list
    devices = []
    suspicious_devices = []
    
    for device_data in data.get("devices", []):
        if "error" in device_data:
            continue
        
        device = NetworkDevice(
            ip=device_data.get("ip", ""),
            mac=device_data.get("mac", "unknown"),
            hostname=device_data.get("hostname"),
            interface=device_data.get("interface", "unknown"),
            is_suspicious=device_data.get("is_suspicious", False),
            suspicious_reasons=device_data.get("suspicious_reasons", []),
            is_known=device_data.get("is_known", False),
        )
        devices.append(device)
        
        if device.is_suspicious:
            suspicious_devices.append(device)
    
    # Convert listening services
    listening = []
    for service_data in data.get("listening", []):
        if "error" in service_data:
            continue
        listening.append(ListeningService(**service_data))
    
    # Convert suspicious connections
    suspicious_conns = []
    for conn_data in data.get("suspicious", []):
        if "error" in conn_data:
            continue
        suspicious_conns.append(SuspiciousConnection(**conn_data))
    
    # Convert interfaces
    interfaces = []
    for iface_data in data.get("interfaces", []):
        if "error" in iface_data:
            continue
        interfaces.append(NetworkInterface(**iface_data))
    
    # Convert auth failures
    auth_data = data.get("auth", {})
    auth = AuthFailure(
        window_minutes=auth_data.get("window_minutes", 10),
        count=auth_data.get("count", 0),
        recent_events=auth_data.get("recent_events", []),
    )
    
    # Convert WiFi status
    wifi_data = data.get("wifi", {})
    wifi = WiFiStatus(**wifi_data)
    
    # Convert latency probes
    latency = []
    for probe_data in data.get("latency", []):
        if "error" in probe_data:
            continue
        latency.append(LatencyProbe(**probe_data))
    
    return NetworkMonitoringReport(
        generated_at=data.get("generated_at", datetime.utcnow().isoformat() + "Z"),
        auth=auth,
        listening=listening,
        suspicious=suspicious_conns,
        devices=devices,
        suspicious_devices=suspicious_devices,
        suspicious_device_count=len(suspicious_devices),
        interfaces=interfaces,
        wifi=wifi,
        latency=latency,
    )


@router.post("/refresh")
async def refresh_network_data() -> Dict[str, Any]:
    """Trigger a refresh of network monitoring data."""
    success = _run_network_watch_script()
    
    if success:
        return {
            "status": "success",
            "message": "Network data refreshed successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh network data. Check server logs for details.",
        )


@router.get("/devices")
async def get_network_devices(refresh: bool = False) -> Dict[str, Any]:
    """Get list of network devices (simplified endpoint)."""
    report = await get_network_status(refresh=refresh)
    
    return {
        "total_devices": len(report.devices),
        "suspicious_devices": len(report.suspicious_devices),
        "devices": [device.model_dump() for device in report.devices],
        "suspicious": [device.model_dump() for device in report.suspicious_devices],
        "generated_at": report.generated_at,
    }


@router.get("/interfaces")
async def get_network_interfaces(refresh: bool = False) -> Dict[str, Any]:
    """Get network interface statistics."""
    report = await get_network_status(refresh=refresh)
    
    return {
        "interfaces": [iface.model_dump() for iface in report.interfaces],
        "generated_at": report.generated_at,
    }


@router.get("/known-devices")
async def get_known_devices() -> Dict[str, Any]:
    """Get list of known/trusted devices."""
    known_devices = _load_known_devices()
    return {
        "hostnames": known_devices.get("hostnames", []),
        "mac_addresses": known_devices.get("mac_addresses", []),
        "ips": known_devices.get("ips", []),
        "blocked_devices": known_devices.get("blocked_devices", []),
    }


@router.post("/known-devices/add")
async def add_known_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """Add a device to the known devices list."""
    known_devices = _load_known_devices()
    
    hostname = device.get("hostname")
    mac = device.get("mac")
    ip = device.get("ip")
    
    if hostname and hostname not in known_devices.get("hostnames", []):
        known_devices.setdefault("hostnames", []).append(hostname)
    
    if mac and mac not in known_devices.get("mac_addresses", []):
        known_devices.setdefault("mac_addresses", []).append(mac)
    
    if ip and ip not in known_devices.get("ips", []):
        known_devices.setdefault("ips", []).append(ip)
    
    # Remove from blocked if it was there
    if "blocked_devices" in known_devices:
        known_devices["blocked_devices"] = [
            d for d in known_devices["blocked_devices"]
            if d.get("hostname") != hostname and d.get("mac") != mac and d.get("ip") != ip
        ]
    
    _save_known_devices(known_devices)
    
    return {
        "status": "success",
        "message": "Device added to known devices",
        "known_devices": known_devices,
    }


@router.post("/known-devices/remove")
async def remove_known_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """Remove a device from the known devices list."""
    known_devices = _load_known_devices()
    
    hostname = device.get("hostname")
    mac = device.get("mac")
    ip = device.get("ip")
    
    if hostname and hostname in known_devices.get("hostnames", []):
        known_devices["hostnames"].remove(hostname)
    
    if mac and mac in known_devices.get("mac_addresses", []):
        known_devices["mac_addresses"].remove(mac)
    
    if ip and ip in known_devices.get("ips", []):
        known_devices["ips"].remove(ip)
    
    _save_known_devices(known_devices)
    
    return {
        "status": "success",
        "message": "Device removed from known devices",
        "known_devices": known_devices,
    }


@router.post("/devices/block")
async def block_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """Block a device (add to blocked list and remove from known)."""
    known_devices = _load_known_devices()
    
    blocked_device = {
        "hostname": device.get("hostname"),
        "mac": device.get("mac"),
        "ip": device.get("ip"),
        "blocked_at": datetime.utcnow().isoformat() + "Z",
        "reason": device.get("reason", "Manually blocked"),
    }
    
    known_devices.setdefault("blocked_devices", []).append(blocked_device)
    
    # Remove from known devices
    hostname = device.get("hostname")
    mac = device.get("mac")
    ip = device.get("ip")
    
    if hostname and hostname in known_devices.get("hostnames", []):
        known_devices["hostnames"].remove(hostname)
    if mac and mac in known_devices.get("mac_addresses", []):
        known_devices["mac_addresses"].remove(mac)
    if ip and ip in known_devices.get("ips", []):
        known_devices["ips"].remove(ip)
    
    _save_known_devices(known_devices)
    
    return {
        "status": "success",
        "message": "Device blocked",
        "blocked_device": blocked_device,
    }


@router.post("/devices/unblock")
async def unblock_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """Unblock a device (remove from blocked list)."""
    known_devices = _load_known_devices()
    
    if "blocked_devices" not in known_devices:
        raise HTTPException(status_code=404, detail="No blocked devices found")
    
    hostname = device.get("hostname")
    mac = device.get("mac")
    ip = device.get("ip")
    
    original_count = len(known_devices["blocked_devices"])
    known_devices["blocked_devices"] = [
        d for d in known_devices["blocked_devices"]
        if not (
            (hostname and d.get("hostname") == hostname) or
            (mac and d.get("mac") == mac) or
            (ip and d.get("ip") == ip)
        )
    ]
    
    if len(known_devices["blocked_devices"]) == original_count:
        raise HTTPException(status_code=404, detail="Device not found in blocked list")
    
    _save_known_devices(known_devices)
    
    return {
        "status": "success",
        "message": "Device unblocked",
    }


@router.get("/config")
async def get_network_config() -> Dict[str, Any]:
    """Get network monitoring configuration."""
    config_file = LOG_DIR / "network_config.json"
    
    # Default configuration
    default_config = {
        "scan_interval_seconds": 60,
        "auto_refresh_enabled": False,
        "alert_on_suspicious": True,
        "alert_threshold": {
            "suspicious_devices": 1,
            "auth_failures": 10,
        },
        "monitoring_settings": {
            "window_minutes": 10,
            "enable_device_detection": True,
            "enable_interface_monitoring": True,
            "enable_wifi_monitoring": True,
        },
        "suspicious_patterns": SUSPICIOUS_HOSTNAME_PATTERNS,
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                # Merge saved config with defaults to ensure all fields are present
                default_config.update(saved_config)
                # Deep merge nested objects
                if "alert_threshold" in saved_config:
                    default_config["alert_threshold"].update(saved_config["alert_threshold"])
                if "monitoring_settings" in saved_config:
                    default_config["monitoring_settings"].update(saved_config["monitoring_settings"])
                return default_config
        except (json.JSONDecodeError, IOError):
            pass
    
    return default_config


@router.post("/config")
async def update_network_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Update network monitoring configuration."""
    config_file = LOG_DIR / "network_config.json"
    
    # Load existing config
    existing_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Deep merge nested objects
    if "alert_threshold" in config and "alert_threshold" in existing_config:
        existing_config["alert_threshold"].update(config["alert_threshold"])
        config = {k: v for k, v in config.items() if k != "alert_threshold"}
    
    if "monitoring_settings" in config and "monitoring_settings" in existing_config:
        existing_config["monitoring_settings"].update(config["monitoring_settings"])
        config = {k: v for k, v in config.items() if k != "monitoring_settings"}
    
    # Merge remaining config
    existing_config.update(config)
    
    # Save
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    return {
        "status": "success",
        "message": "Configuration updated",
        "config": existing_config,
    }


@router.post("/devices/update")
async def update_device(device_update: Dict[str, Any]) -> Dict[str, Any]:
    """Update device information (hostname, category, notes, etc.)."""
    device_metadata_file = LOG_DIR / "device_metadata.json"
    
    # Load existing device metadata
    device_metadata = {}
    if device_metadata_file.exists():
        try:
            with open(device_metadata_file, 'r') as f:
                device_metadata = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Use MAC as primary key, fallback to IP
    device_key = device_update.get("mac") or device_update.get("ip") or "unknown"
    
    if device_key not in device_metadata:
        device_metadata[device_key] = {}
    
    # Update device metadata
    if "hostname" in device_update:
        device_metadata[device_key]["custom_hostname"] = device_update["hostname"]
    if "category" in device_update:
        device_metadata[device_key]["category"] = device_update["category"]
    if "notes" in device_update:
        device_metadata[device_key]["notes"] = device_update["notes"]
    if "ip" in device_update:
        device_metadata[device_key]["custom_ip"] = device_update["ip"]
    if "mac" in device_update:
        device_metadata[device_key]["mac"] = device_update["mac"]
    
    device_metadata[device_key]["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    # Save
    device_metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(device_metadata_file, 'w') as f:
        json.dump(device_metadata, f, indent=2)
    
    return {
        "status": "success",
        "message": "Device updated",
        "device": device_metadata[device_key],
    }


@router.get("/devices/metadata")
async def get_device_metadata() -> Dict[str, Any]:
    """Get all device metadata (custom hostnames, categories, notes)."""
    device_metadata_file = LOG_DIR / "device_metadata.json"
    
    if device_metadata_file.exists():
        try:
            with open(device_metadata_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    return {}


@router.get("/recommended-settings")
async def get_recommended_settings() -> Dict[str, Any]:
    """Get recommended network security and performance settings."""
    return {
        "security": {
            "recommendations": [
                {
                    "title": "Enable MAC Address Filtering",
                    "description": "Only allow known devices to connect to your network",
                    "priority": "high",
                    "category": "security",
                    "action": "router_config",
                },
                {
                    "title": "Change Default Router Password",
                    "description": "Use a strong, unique password for router admin access",
                    "priority": "critical",
                    "category": "security",
                    "action": "router_config",
                },
                {
                    "title": "Use WPA3 or WPA2-AES Encryption",
                    "description": "Enable the strongest WiFi encryption available",
                    "priority": "high",
                    "category": "security",
                    "action": "router_config",
                },
                {
                    "title": "Disable WPS",
                    "description": "WPS is vulnerable to brute-force attacks",
                    "priority": "high",
                    "category": "security",
                    "action": "router_config",
                },
                {
                    "title": "Change Default DNS Servers",
                    "description": "Use Cloudflare (1.1.1.1) or Google (8.8.8.8) for better privacy and speed",
                    "priority": "medium",
                    "category": "performance",
                    "action": "router_config",
                },
                {
                    "title": "Optimize WiFi Channels",
                    "description": "Use non-overlapping channels (1, 6, 11 for 2.4GHz) to reduce interference",
                    "priority": "medium",
                    "category": "performance",
                    "action": "router_config",
                },
                {
                    "title": "Enable Firewall",
                    "description": "Ensure router firewall is enabled with SPI (Stateful Packet Inspection)",
                    "priority": "high",
                    "category": "security",
                    "action": "router_config",
                },
                {
                    "title": "Disable UPnP",
                    "description": "Prevents apps from automatically opening ports (security risk)",
                    "priority": "medium",
                    "category": "security",
                    "action": "router_config",
                },
            ],
            "scan_interval_seconds": 60,
            "alert_on_suspicious": True,
            "alert_threshold": {
                "suspicious_devices": 1,
                "auth_failures": 5,
            },
        },
        "performance": {
            "recommendations": [
                {
                    "title": "Optimize Channel Selection",
                    "description": "Use WiFi analyzer to find least crowded channels",
                    "priority": "medium",
                    "category": "performance",
                },
                {
                    "title": "Enable QoS",
                    "description": "Prioritize gaming/streaming traffic for better performance",
                    "priority": "low",
                    "category": "performance",
                },
                {
                    "title": "Use 5GHz for High-Speed Devices",
                    "description": "Connect fast devices to 5GHz network for maximum speed",
                    "priority": "low",
                    "category": "performance",
                },
            ],
        },
        "monitoring": {
            "window_minutes": 10,
            "auto_refresh_enabled": False,
            "enable_device_detection": True,
            "enable_interface_monitoring": True,
        },
    }





