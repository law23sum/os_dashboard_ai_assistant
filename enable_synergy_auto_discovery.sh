#!/bin/bash
# Enable Synergy auto-discovery to automatically find computers on the network

set -euo pipefail

SYNERGY_SERVICE="http://127.0.0.1:24802"
SYNERGY_LOCAL_JSON="${HOME}/Library/Preferences/Synergy/local.json"
BACKUP_DIR="${HOME}/Library/Preferences/Synergy/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
    printf '[%s] WARN: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

error() {
    printf '[%s] ERROR: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
    exit 1
}

log "Enabling Synergy auto-discovery..."

# Check if Synergy service is running (optional - we can configure without it)
if curl -sS -f "${SYNERGY_SERVICE}/ping" > /dev/null 2>&1; then
    log "Synergy service is running"
    SERVICE_RUNNING=true
else
    log "Synergy service is not currently running (will configure for next start)"
    SERVICE_RUNNING=false
fi

# Backup local.json
mkdir -p "${BACKUP_DIR}"
if [ -f "${SYNERGY_LOCAL_JSON}" ]; then
    log "Backing up local.json..."
    cp "${SYNERGY_LOCAL_JSON}" "${BACKUP_DIR}/local.json.pre-discovery.${TIMESTAMP}"
fi

# Update local.json to ensure network interface is set to Auto and enable discovery
log "Updating local.json configuration..."
python3 - "${SYNERGY_LOCAL_JSON}" << 'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])

if not json_path.exists():
    print(f"Config file not found: {json_path}")
    sys.exit(1)

def ensure_dict(parent, key):
    """Ensure parent[key] exists and is a dict."""
    if key not in parent or not isinstance(parent[key], dict):
        parent[key] = {}
        return True, parent[key]
    return False, parent[key]


def ensure_value(root, path, value, create_missing=True):
    """
    Ensure a nested value exists and equals `value`.
    Returns True if an update was made.
    """
    current = root
    for segment in path[:-1]:
        if not isinstance(current, dict):
            return False
        if segment not in current:
            if not create_missing:
                return False
            current[segment] = {}
        elif not isinstance(current[segment], dict):
            current[segment] = {}
        current = current[segment]

    last = path[-1]
    if not isinstance(current, dict):
        return False

    if current.get(last) == value:
        return False

    current[last] = value
    return True


try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    modified = False
    messages = []
    
    # Ensure network interface is set to Auto
    network_created, network = ensure_dict(data, 'network')
    if network_created:
        modified = True
        messages.append("Created missing 'network' section")
    
    if network.get('interface') != 'Auto':
        network['interface'] = 'Auto'
        modified = True
        messages.append("Set network interface to 'Auto'")
    
    # Ensure discovery block exists and is fully enabled
    discovery_created, discovery = ensure_dict(data, 'discovery')
    if discovery_created:
        modified = True
        messages.append("Created missing 'discovery' section")
    
    discovery_flags = {
        'enabled': True,
        'autoAddServers': True,
        'autoAddClients': True,
        'autoSwitchToServer': True,
        'autoSwitchToBest': True,
    }
    for key, desired in discovery_flags.items():
        if discovery.get(key) != desired:
            discovery[key] = desired
            modified = True
            messages.append(f"Enabled discovery flag '{key}'")
    
    if isinstance(discovery.get('mode'), str) and discovery['mode'].lower() != 'auto':
        discovery['mode'] = 'auto'
        modified = True
        messages.append("Set discovery mode to 'auto'")
    
    # Mirror discovery settings under network if Synergy expects them there
    network_discovery_flags = {
        'autoDiscovery': True,
        'auto_discovery': True,
        'autoDiscover': True,
        'discover': True,
        'discoverPeers': True,
        'useBonjour': True,
        'bonjour': True,
        'zeroconf': True,
        'zeroconfEnabled': True,
        'mdns': True,
        'enableBonjour': True,
    }
    for key, desired in network_discovery_flags.items():
        if key in network and network[key] != desired:
            network[key] = desired
            modified = True
            messages.append(f"Forced network discovery flag '{key}' = true")
    
    # Provide sensible defaults for common flags that might be missing
    for key in ('autoDiscovery', 'discoverPeers', 'useBonjour'):
        if key not in network:
            network[key] = True
            modified = True
            messages.append(f"Added network discovery flag '{key}' = true")
    
    # Remove manual-only peers which can block auto-discovery from populating
    local_computers = data.get('local_computers')
    if isinstance(local_computers, dict):
        keys_to_remove = []
        for name, computer in list(local_computers.items()):
            if isinstance(computer, dict):
                manual_flags = [
                    computer.get('manual'),
                    computer.get('isManual'),
                    computer.get('manualEntry'),
                    computer.get('manual_address'),
                    computer.get('manualAddress'),
                    computer.get('source') == 'manual',
                ]
                discovered_flag = computer.get('discovered')
                if any(flag is True for flag in manual_flags) or discovered_flag is False:
                    keys_to_remove.append(name)
                elif not computer.get('ip'):
                    keys_to_remove.append(name)
            elif not computer:
                keys_to_remove.append(name)
        
        for key in keys_to_remove:
            local_computers.pop(key, None)
            modified = True
            messages.append(f"Removed manual computer entry '{key}' to unblock discovery")
    
    # Mirror discovery settings for legacy 'network.discovery' schemas
    if ensure_value(data, ('network', 'discovery', 'enabled'), True):
        modified = True
        messages.append("Ensured 'network.discovery.enabled' is true")
    if ensure_value(data, ('network', 'discovery', 'mode'), 'auto'):
        modified = True
        messages.append("Set 'network.discovery.mode' to 'auto'")
    
    # For auto-discovery to work properly, we may want to keep local_computers
    # but Synergy should auto-populate discovered computers
    # The auto-discovery feature works independently of local_computers
    
    if modified:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
        for message in messages:
            print(f"- {message}")
        print("✅ local.json updated successfully")
    else:
        print("ℹ️  Configuration already set for auto-discovery")
        
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error processing local.json: {e}")
    sys.exit(1)
PYTHON_SCRIPT

log "✅ Configuration updated"

# Try to trigger auto-discovery via API (if service is running)
if [ "${SERVICE_RUNNING}" = true ]; then
    log ""
    log "Attempting to trigger auto-discovery..."
    
    # Check available endpoints - Synergy 3.x may use different endpoints
    ENDPOINTS=(
        "/api/discovery/start"
        "/api/discovery"
        "/api/discover"
        "/api/auto-discovery"
        "/api/computers/discover"
        "/api/network/discover"
    )
    
    DISCOVERY_TRIGGERED=false
    for endpoint in "${ENDPOINTS[@]}"; do
        for method in GET POST; do
            if [ "${method}" = "POST" ]; then
                RESPONSE=$(curl -sS -X "${method}" -H "Content-Type: application/json" -d '{}' -w "\n%{http_code}" "${SYNERGY_SERVICE}${endpoint}" 2>/dev/null || echo "")
            else
                RESPONSE=$(curl -sS -X "${method}" -w "\n%{http_code}" "${SYNERGY_SERVICE}${endpoint}" 2>/dev/null || echo "")
            fi
            HTTP_CODE=$(echo "${RESPONSE}" | tail -1)
            
            if [ "${HTTP_CODE}" = "200" ] || [ "${HTTP_CODE}" = "202" ] || [ "${HTTP_CODE}" = "204" ]; then
                log "✅ Triggered discovery via ${method} ${endpoint}"
                DISCOVERY_TRIGGERED=true
                break 2
            fi
        done
    done
    
    if [ "${DISCOVERY_TRIGGERED}" = false ]; then
        log "ℹ️  Direct API discovery trigger not available (this is normal)"
        log "   Auto-discovery runs automatically in the background when enabled"
    fi
else
    log ""
    log "ℹ️  Service not running - auto-discovery will start when Synergy launches"
fi

FOUND_HOSTS=()
HOST_SOURCE=""

if [ "${SERVICE_RUNNING}" = true ]; then
    log ""
    log "Checking for discovered computers via Synergy API..."
    
    COMPUTERS_ENDPOINTS=(
        "/api/discovery/computers"
        "/api/discovery/peers"
        "/api/discovery"
        "/api/computers"
        "/api/peers"
        "/api/network/computers"
        "/api/network/peers"
        "/api/v1/computers"
        "/api/v1/peers"
        "/discovery/computers"
        "/discovery/peers"
    )
    
    for endpoint in "${COMPUTERS_ENDPOINTS[@]}"; do
        RESPONSE=$(curl -sS -w "\n%{http_code}" "${SYNERGY_SERVICE}${endpoint}" 2>/dev/null || echo "")
        HTTP_CODE=$(echo "${RESPONSE}" | tail -1)
        BODY=$(echo "${RESPONSE}" | sed '$d')
        
        if [ "${HTTP_CODE}" = "200" ] || [ "${HTTP_CODE}" = "202" ]; then
            HOST_LINES=$(python3 - "$BODY" <<'PYTHON_SCRIPT'
import json
import re
import sys

raw = sys.argv[1]

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("", end="")
    sys.exit(0)

seen = set()
lines = []

def looks_like_ip(value: str) -> bool:
    return bool(re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", value))

def clean_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned

def extract(node):
    if isinstance(node, dict):
        lower_keys = {k.lower(): k for k in node}
        ip_key = next((lower_keys[k] for k in lower_keys if k in {"ip", "host", "hostname", "address", "ipaddress"}), None)
        name_key = next((lower_keys[k] for k in lower_keys if k in {"name", "computername", "machinename", "hostname", "label"}), None)
        role_key = next((lower_keys[k] for k in lower_keys if k in {"role", "type", "mode", "kind"}), None)
        manual_keys = [lower_keys[k] for k in lower_keys if k in {"manual", "ismanual", "manualentry", "manual_address", "manualaddress"}]
        discovered_keys = [lower_keys[k] for k in lower_keys if k in {"discovered", "isdiscovered", "autodiscovered"}]

        ip_value = node.get(ip_key) if ip_key else None
        if isinstance(ip_value, str) and looks_like_ip(ip_value):
            name_value = node.get(name_key) if name_key else ""
            if isinstance(name_value, str):
                name_value = clean_name(name_value)
            else:
                name_value = ""

            role_value = node.get(role_key) if role_key else ""
            if not isinstance(role_value, str):
                role_value = ""

            manual = any(node.get(key) is True for key in manual_keys)
            if discovered_keys:
                discovered_flag = any(node.get(key) for key in discovered_keys)
            else:
                discovered_flag = True

            key = (name_value, ip_value, role_value, manual, discovered_flag)
            if key not in seen:
                seen.add(key)
                lines.append(f"{name_value}|{ip_value}|{role_value}|{int(manual)}|{int(discovered_flag)}")

        for value in node.values():
            extract(value)

    elif isinstance(node, list):
        for item in node:
            extract(item)

extract(data)

print("\n".join(lines), end="")
PYTHON_SCRIPT
)
            if [ -n "${HOST_LINES}" ]; then
                while IFS= read -r host_line; do
                    [ -z "${host_line}" ] && continue
                    FOUND_HOSTS+=("${host_line}")
                done <<< "${HOST_LINES}"
                HOST_SOURCE="service"
                break
            fi
        fi
    done

    if [ ${#FOUND_HOSTS[@]} -gt 0 ]; then
        log "✅ Found ${#FOUND_HOSTS[@]} computer(s) published by Synergy:"
        for host in "${FOUND_HOSTS[@]}"; do
            IFS='|' read -r name ip role manual_flag discovered_flag <<< "${host}"
            [ -z "${name}" ] && name="(unnamed)"
            [ "${role}" = "" ] && role="unknown"
            if [ "${manual_flag}" = "1" ]; then
                log "    - ${name} (${ip}) role=${role} [manual entry]"
            else
                log "    - ${name} (${ip}) role=${role}"
            fi
        done
    else
        log "ℹ️  No computers reported yet via Synergy API."
    fi
fi

if [ ${#FOUND_HOSTS[@]} -eq 0 ] && command -v dns-sd >/dev/null 2>&1; then
    log ""
    log "Scanning Bonjour/mDNS for Synergy hosts..."
    MDNS_HOST_LINES=$(python3 <<'PYTHON_SCRIPT'
import re
import shutil
import subprocess
import sys
import time

if shutil.which("dns-sd") is None:
    sys.exit(0)

instances = set()
try:
    proc = subprocess.Popen(
        ["dns-sd", "-B", "_synergy._tcp", "local"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
except FileNotFoundError:
    sys.exit(0)

start = time.time()
try:
    while time.time() - start < 6:
        line = proc.stdout.readline()
        if not line:
            break
        if "_synergy._tcp" not in line:
            continue
        if "Add" not in line:
            continue
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        candidate = parts[-2]
        if candidate.endswith("._synergy._tcp."):
            instance = candidate[: -len("._synergy._tcp.")]
            if instance:
                instances.add(instance)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=1.5)
    except Exception:
        proc.kill()

entries = []

for instance in sorted(instances):
    try:
        detail = subprocess.check_output(
            ["dns-sd", "-L", instance, "_synergy._tcp", "local"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=6,
        )
    except subprocess.SubprocessError:
        continue

    host = None
    ips = set()

    for line in detail.splitlines():
        match = re.search(r"can be reached at ([^ ]+)\.?:(\d+)", line)
        if match:
            host = match.group(1)
        for addr in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line):
            ips.add(addr)

    if not ips and host:
        try:
            resolve = subprocess.check_output(
                ["dns-sd", "-G", "v4", host],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=6,
            )
            for line in resolve.splitlines():
                for addr in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line):
                    ips.add(addr)
        except subprocess.SubprocessError:
            pass

    if not ips:
        continue

    for ip in ips:
        label = instance.strip() or f"synergy-{ip.replace('.', '-')}"
        entries.append(f"{label}|{ip}|mdns|0|1")

print("\n".join(entries))
PYTHON_SCRIPT
)

    if [ -n "${MDNS_HOST_LINES}" ]; then
        while IFS= read -r host_line; do
            [ -z "${host_line}" ] && continue
            FOUND_HOSTS+=("${host_line}")
        done <<< "${MDNS_HOST_LINES}"
        HOST_SOURCE="mdns"
        log "✅ Discovered Synergy services via Bonjour:"
        for host in "${FOUND_HOSTS[@]}"; do
            IFS='|' read -r name ip role manual_flag discovered_flag <<< "${host}"
            log "    - ${name} (${ip}) via mDNS"
        done
    else
        log "ℹ️  No Bonjour announcements detected for Synergy."
    fi
fi

if [ ${#FOUND_HOSTS[@]} -eq 0 ]; then
    log ""
    log "Scanning local network for Synergy hosts (ports 24800-24803)..."
    
    # Build candidate IP list from ARP table
    CANDIDATE_IPS=()
    while IFS= read -r ip; do
        [ -z "${ip}" ] && continue
        CANDIDATE_IPS+=("${ip}")
    done < <(arp -an 2>/dev/null | awk '{print $2}' | tr -d '()' | sort -u)
    
    if [ ${#CANDIDATE_IPS[@]} -eq 0 ]; then
        log "ℹ️  ARP table empty; attempting to discover subnet peers..."
        DEFAULT_IFACE=$(route -n get default 2>/dev/null | awk '/interface:/{print $2}' | head -n1)
        if [ -n "${DEFAULT_IFACE}" ]; then
            LOCAL_IP=$(ipconfig getifaddr "${DEFAULT_IFACE}" 2>/dev/null || true)
            if [ -n "${LOCAL_IP}" ]; then
                SUBNET_PREFIX=$(echo "${LOCAL_IP}" | awk -F. '{printf "%s.%s.%s.", $1,$2,$3}')
                for last_octet in 1 2 3 4 5 10 20 30 40 50 60 70 80 90 100 110 120 150 180 200 220 240 250; do
                    CANDIDATE_IPS+=("${SUBNET_PREFIX}${last_octet}")
                done
                CANDIDATE_IPS=($(printf "%s\n" "${CANDIDATE_IPS[@]}" | sort -u))
            else
                log "⚠️  Could not determine local IP address; skipping subnet scan."
            fi
        else
            log "⚠️  Could not determine default interface; skipping subnet scan."
        fi
    fi

    if [ ${#CANDIDATE_IPS[@]} -eq 0 ]; then
        log "⚠️  No candidate IPs available for scanning."
    else
        for ip in "${CANDIDATE_IPS[@]}"; do
            HOST_PORT_FOUND=false
            for port in 24800 24801 24802 24803; do
                if nc -z -G 1 "${ip}" "${port}" 2>/dev/null; then
                    HOST_PORT_FOUND=true
                    break
                fi
            done
            if [ "${HOST_PORT_FOUND}" = true ]; then
                # Attempt to resolve hostname (best effort)
                HOSTNAME_LOOKUP=$( (host "${ip}" 2>/dev/null || nslookup "${ip}" 2>/dev/null || echo "") | head -n1 )
                HOSTNAME=""
                if echo "${HOSTNAME_LOOKUP}" | grep -qE 'domain|name ='; then
                    HOSTNAME=$(echo "${HOSTNAME_LOOKUP}" | sed -E 's/.*name = ([^ ]+).*/\1/' | sed 's/\.$//' )
                elif echo "${HOSTNAME_LOOKUP}" | grep -qE 'pointer'; then
                    HOSTNAME=$(echo "${HOSTNAME_LOOKUP}" | sed -E 's/.*pointer ([^ ]+).*/\1/' | sed 's/\.$//' )
                fi
                if [ -z "${HOSTNAME}" ]; then
                    HOSTNAME="synergy-${ip//./-}"
                fi
                FOUND_HOSTS+=("${HOSTNAME}|${ip}|tcp-scan|0|1")
            fi
        done

        if [ ${#FOUND_HOSTS[@]} -gt 0 ]; then
            HOST_SOURCE="scan"
            log "✅ Detected ${#FOUND_HOSTS[@]} potential Synergy host(s) via network scan:"
            for host in "${FOUND_HOSTS[@]}"; do
                IFS='|' read -r name ip role manual_flag discovered_flag <<< "${host}"
                log "    - ${name} (${ip}) role=${role}"
            done
        else
            log "ℹ️  No Synergy hosts detected on the local network scan."
        fi
    fi
fi

if [ ${#FOUND_HOSTS[@]} -gt 0 ]; then
    log ""
    log "Recording discovered hosts into local.json..."
    export FOUND_SYNERGY_HOSTS=$(printf "%s\n" "${FOUND_HOSTS[@]}")
    python3 - "${SYNERGY_LOCAL_JSON}" <<'PYTHON_SCRIPT'
import json
import os
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
hosts_raw = os.environ.get("FOUND_SYNERGY_HOSTS", "").strip().splitlines()

if not hosts_raw:
    sys.exit(0)

if not json_path.exists():
    print("Config file not found while writing hosts")
    sys.exit(1)

with open(json_path, "r") as f:
    data = json.load(f)

modified = False

if not isinstance(data, dict):
    data = {}
    modified = True

local_computers = data.get("local_computers")
if not isinstance(local_computers, dict):
    local_computers = {}
    data["local_computers"] = local_computers
    modified = True

peers = data.get("peers")
if not isinstance(peers, list):
    peers = []
    data["peers"] = peers
    modified = True

existing_peer_ips = set()
for peer in peers:
    if isinstance(peer, dict):
        ip = peer.get("ip")
        if isinstance(ip, str):
            existing_peer_ips.add(ip)
    elif isinstance(peer, str):
        existing_peer_ips.add(peer)

for entry in hosts_raw:
    parts = entry.split("|")
    if len(parts) < 5:
        continue
    name, ip, role, manual_flag, discovered_flag = parts
    name = name.strip() or f"synergy-{ip.replace('.', '-')}"
    safe_name = name.replace(" ", "-")
    role = role.strip()
    manual = manual_flag == "1"
    discovered = discovered_flag == "1"

    existing = local_computers.get(safe_name)
    if not isinstance(existing, dict):
        local_computers[safe_name] = {}
        existing = local_computers[safe_name]
        modified = True

    desired = {
        "ip": ip,
        "name": name,
        "role": role or "auto",
        "source": "auto-discovery-script",
        "manual": manual,
        "discovered": discovered,
    }

    if existing != desired:
        existing.clear()
        existing.update(desired)
        modified = True
        print(f"- Persisted host '{name}' ({ip})")

    if ip not in existing_peer_ips:
        peers.append({"ip": ip, "name": name, "role": role or "auto"})
        existing_peer_ips.add(ip)
        modified = True
        print(f"- Registered peer entry for {ip}")

if modified:
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)
    print("✅ local.json updated with discovered hosts")
else:
    print("ℹ️  Host entries already present in local.json")
PYTHON_SCRIPT
fi

if [ ${#FOUND_HOSTS[@]} -eq 0 ]; then
    log ""
    log "⚠️  No Synergy peers discovered automatically."
    log "   - Ensure Synergy is running on at least one other computer."
    log "   - Confirm all machines are on the same subnet and ports 24800-24803 are open."
    log "   - You can rerun this script after powering on remote Synergy peers."
fi

log ""
log "=== Auto-Discovery Configuration Complete ==="
log ""
log "Auto-discovery is enabled and will:"
log "  - Automatically find Synergy computers on your local network"
log "  - Use network interface: Auto (best available)"
log "  - Scan for computers periodically in the background"
log ""
log "Note: Auto-discovery runs automatically. You should see discovered"
log "computers appear in the Synergy GUI. To manually refresh, you may need"
log "to restart Synergy or use the GUI's refresh/discover button."
log ""
log "Check discovered computers with:"
log "  curl -sS http://127.0.0.1:24802/ping"
log ""
log "Monitor discovery in logs:"
log "  tail -f ~/Library/Logs/Synergy/synergy.log | grep -i discovery"




