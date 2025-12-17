#!/bin/bash
# Fix Synergy crash loop on macOS by disabling problematic mouse features
# and removing stale peer configuration

set -euo pipefail

SYNERGY_PREFS_DIR="${HOME}/Library/Preferences/Synergy"
SYNERGY_CONF="${SYNERGY_PREFS_DIR}/synergy.conf"
SYNERGY_LOCAL_JSON="${SYNERGY_PREFS_DIR}/local.json"
SYNERGY_LOG="${HOME}/Library/Logs/Synergy/synergy.log"
BACKUP_DIR="${HOME}/Library/Preferences/Synergy/backups"

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

# Create backup directory
mkdir -p "${BACKUP_DIR}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log "Starting Synergy crash loop fix..."
log "Backup directory: ${BACKUP_DIR}"

# Step A: Backup and fix synergy.conf
if [ -f "${SYNERGY_CONF}" ]; then
    log "Backing up synergy.conf..."
    cp "${SYNERGY_CONF}" "${BACKUP_DIR}/synergy.conf.${TIMESTAMP}"
    
    log "Modifying synergy.conf to disable problematic mouse features..."
    
    # Use Python for reliable config file manipulation
    python3 - "${SYNERGY_CONF}" << 'PYTHON_SCRIPT'
import re
import sys
from pathlib import Path

conf_path = Path(sys.argv[1])

if not conf_path.exists():
    print(f"Config file not found: {conf_path}")
    sys.exit(1)

content = conf_path.read_text()

# Find the options section and update/insert the problematic settings
options_section_pattern = r'(section:\s+options\s*)(.*?)(end)'
match = re.search(options_section_pattern, content, re.DOTALL | re.IGNORECASE)

if match:
    section_start = match.group(1)
    section_body = match.group(2)
    section_end = match.group(3)
    
    # Remove existing relativeMouseMoves and disableLockToScreen lines
    section_body = re.sub(r'^\s*relativeMouseMoves\s*=.*$', '', section_body, flags=re.MULTILINE | re.IGNORECASE)
    section_body = re.sub(r'^\s*disableLockToScreen\s*=.*$', '', section_body, flags=re.MULTILINE | re.IGNORECASE)
    
    # Add the fixed settings (relativeMouseMoves = false, disableLockToScreen = true)
    # Insert before any existing settings, preserving other settings
    if not re.search(r'relativeMouseMoves', section_body, re.IGNORECASE):
        section_body = "    relativeMouseMoves = false\n" + section_body
    if not re.search(r'disableLockToScreen', section_body, re.IGNORECASE):
        section_body = "    disableLockToScreen = true\n" + section_body
    
    # Reconstruct the section
    content = content[:match.start()] + section_start + section_body + section_end + content[match.end():]
else:
    # If no options section exists, create one
    # Find a good insertion point (before any existing sections or at end)
    if re.search(r'section:', content, re.IGNORECASE):
        # Insert before first section
        first_section = re.search(r'section:', content, re.IGNORECASE)
        options_section = """section: options
    relativeMouseMoves = false
    disableLockToScreen = true
end

"""
        content = content[:first_section.start()] + options_section + content[first_section.start():]
    else:
        # Append to end
        content += """
section: options
    relativeMouseMoves = false
    disableLockToScreen = true
end
"""

conf_path.write_text(content)
print("✅ synergy.conf updated successfully")
PYTHON_SCRIPT
    
    log "✅ synergy.conf updated: relativeMouseMoves = false, disableLockToScreen = true"
else
    warn "synergy.conf not found at ${SYNERGY_CONF}, skipping..."
fi

# Step B: Backup and fix local.json (remove stale peer IP 192.168.254.148)
if [ -f "${SYNERGY_LOCAL_JSON}" ]; then
    log "Backing up local.json..."
    cp "${SYNERGY_LOCAL_JSON}" "${BACKUP_DIR}/local.json.${TIMESTAMP}"
    
    log "Removing stale peer IP 192.168.254.148 from local.json..."
    
    python3 - "${SYNERGY_LOCAL_JSON}" << 'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])

if not json_path.exists():
    print(f"Config file not found: {json_path}")
    sys.exit(1)

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    modified = False
    
    # Check local_computers for the stale IP
    if 'local_computers' in data and isinstance(data['local_computers'], dict):
        # Remove entries that map to 192.168.254.148
        keys_to_remove = []
        for key, value in data['local_computers'].items():
            if isinstance(value, dict) and value.get('ip') == '192.168.254.148':
                keys_to_remove.append(key)
            elif isinstance(value, str) and value == '192.168.254.148':
                keys_to_remove.append(key)
            # Also check if the value itself is the IP
            elif value == '192.168.254.148':
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del data['local_computers'][key]
            modified = True
            print(f"Removed peer entry '{key}' mapping to 192.168.254.148")
    
    # Also check other common locations where IPs might be stored
    if 'peers' in data and isinstance(data['peers'], list):
        original_length = len(data['peers'])
        data['peers'] = [p for p in data['peers'] if p.get('ip') != '192.168.254.148' and p != '192.168.254.148']
        if len(data['peers']) < original_length:
            modified = True
            print(f"Removed {original_length - len(data['peers'])} peer(s) with IP 192.168.254.148")
    
    if modified:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ local.json updated successfully")
    else:
        print("ℹ️  No stale peer IP found in local.json, no changes needed")
        
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error processing local.json: {e}")
    sys.exit(1)
PYTHON_SCRIPT
    
    log "✅ local.json cleaned"
else
    warn "local.json not found at ${SYNERGY_LOCAL_JSON}, skipping..."
fi

# Step C: Kill existing Synergy processes
log "Stopping Synergy processes..."

# Try graceful quit first
if pgrep -x "Synergy" > /dev/null; then
    log "Attempting graceful quit via osascript..."
    osascript -e 'tell application "Synergy" to quit' 2>/dev/null || true
    sleep 2
fi

# Force kill if still running
if pgrep -f "synergy-core" > /dev/null || pgrep -f "synergy-service" > /dev/null; then
    log "Force killing synergy-core and synergy-service processes..."
    pkill -f synergy-core 2>/dev/null || true
    pkill -f synergy-service 2>/dev/null || true
    sleep 1
    
    # Double-check
    if pgrep -f "synergy-core" > /dev/null || pgrep -f "synergy-service" > /dev/null; then
        warn "Some Synergy processes may still be running"
    else
        log "✅ All Synergy processes stopped"
    fi
else
    log "✅ No Synergy processes found running"
fi

# Validation
log ""
log "=== Validation ==="
log "Checking listening ports..."
if command -v lsof > /dev/null; then
    LISTENING=$(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -E 'synergy|2480' || true)
    if [ -n "${LISTENING}" ]; then
        log "Found listening ports:"
        echo "${LISTENING}"
    else
        log "✅ No Synergy-related ports currently listening (expected after kill)"
    fi
else
    warn "lsof not available, skipping port check"
fi

log ""
log "Checking recent log entries..."
if [ -f "${SYNERGY_LOG}" ]; then
    log "Last 20 lines of synergy.log:"
    tail -n 20 "${SYNERGY_LOG}" | sed 's/^/  /'
else
    warn "synergy.log not found at ${SYNERGY_LOG}"
fi

log ""
log "=== Fix Complete ==="
log "✅ Configuration files backed up to: ${BACKUP_DIR}"
log "✅ Configuration updated:"
log "   - relativeMouseMoves = false"
log "   - disableLockToScreen = true"
log "   - Stale peer IP (192.168.254.148) removed"
log ""
log "Next steps:"
log "1. Relaunch Synergy normally from Applications"
log "2. Monitor the log with: tail -f ${SYNERGY_LOG}"
log "3. Verify stability: curl -sS http://127.0.0.1:24802/ping"
log ""
log "If crashes persist, consider:"
log "- Updating Synergy to the latest version"
log "- Trying Barrier (open-source Synergy fork)"
log "- Checking macOS compatibility"


