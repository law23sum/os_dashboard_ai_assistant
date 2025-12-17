#!/bin/bash
# Quick validation script to check if Synergy crash loop is resolved

SYNERGY_LOG="${HOME}/Library/Logs/Synergy/synergy.log"

echo "=== Synergy Fix Validation ==="
echo ""

echo "1. Checking listening ports (should show synergy-service on 24802 if running):"
echo "---"
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -E 'synergy|2480' || echo "No Synergy ports listening"
echo ""

echo "2. Testing HTTP ping endpoint:"
echo "---"
curl -sS -v http://127.0.0.1:24802/ping 2>&1 | head -20 || echo "Connection failed (service may not be running yet)"
echo ""

echo "3. Recent log entries (last 120 lines):"
echo "---"
if [ -f "${SYNERGY_LOG}" ]; then
    tail -n 120 "${SYNERGY_LOG}"
else
    echo "Log file not found: ${SYNERGY_LOG}"
fi
echo ""

echo "4. Checking for crash keywords in recent logs:"
echo "---"
if [ -f "${SYNERGY_LOG}" ]; then
    CRASH_KEYWORDS=$(tail -n 200 "${SYNERGY_LOG}" | grep -iE "terminating|exception|crash|segfault|EXC_BAD_ACCESS|SIGSEGV" | tail -5 || true)
    if [ -n "${CRASH_KEYWORDS}" ]; then
        echo "⚠️  Found potential crash indicators:"
        echo "${CRASH_KEYWORDS}"
    else
        echo "✅ No recent crash indicators found"
    fi
else
    echo "Log file not found"
fi
echo ""

echo "5. Current Synergy processes:"
echo "---"
ps aux | grep -E 'synergy|Synergy' | grep -v grep || echo "No Synergy processes running"
echo ""

echo "=== Validation Complete ==="


