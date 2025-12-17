#!/bin/bash
# Opens macOS Terminal, starts an SSH session to the specified host, and surfaces local guides.

set -euo pipefail

TARGET="${1:-mac-mini}"
GUIDE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/mac_mini_sync_guides.md"

if ! command -v osascript >/dev/null 2>&1; then
  echo "osascript not available; this helper requires macOS. You can still run 'ssh ${TARGET}' manually." >&2
  exit 1
fi

osascript <<EOF
tell application "Terminal"
    activate
    do script "ssh ${TARGET}"
end tell
EOF

if [[ -f "${GUIDE_PATH}" ]]; then
  open "${GUIDE_PATH}" >/dev/null 2>&1 || true
else
  echo "Guide file not found at ${GUIDE_PATH}. Create it to surface tutorials automatically." >&2
fi
