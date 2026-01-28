#!/bin/bash
# Run all verification scripts

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=================================================================================="
echo "Running All Verifications"
echo "=================================================================================="
echo ""

# Make scripts executable
chmod +x scripts/*.py 2>/dev/null || true

# Run verifications
echo "1. IA Compliance Verification..."
python3 scripts/verify_ia_compliance.py
IA_RESULT=$?
echo ""

echo "2. Actor Switch Verification..."
python3 scripts/verify_actor_switch.py
ACTOR_RESULT=$?
echo ""

echo "3. Duplicate Routes Verification..."
python3 scripts/verify_no_duplicates.py
DUPLICATE_RESULT=$?
echo ""

echo "4. Page Existence Verification..."
python3 scripts/verify_pages_exist.py
PAGES_RESULT=$?
echo ""

echo "=================================================================================="
echo "Verification Summary"
echo "=================================================================================="

TOTAL_FAILED=0

if [ $IA_RESULT -eq 0 ]; then
    echo "✅ IA Compliance: PASSED"
else
    echo "❌ IA Compliance: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $ACTOR_RESULT -eq 0 ]; then
    echo "✅ Actor Switch: PASSED"
else
    echo "❌ Actor Switch: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $DUPLICATE_RESULT -eq 0 ]; then
    echo "✅ No Duplicates: PASSED"
else
    echo "❌ No Duplicates: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $PAGES_RESULT -eq 0 ]; then
    echo "✅ Pages Exist: PASSED"
else
    echo "❌ Pages Exist: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo ""
if [ $TOTAL_FAILED -eq 0 ]; then
    echo "✅ All Verifications PASSED"
    exit 0
else
    echo "❌ $TOTAL_FAILED verification(s) FAILED"
    exit 1
fi




