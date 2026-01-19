#!/bin/bash
# Run All Tests (Backend + Frontend)
# Usage: ./scripts/run_all_tests.sh [--env ENV] [--full|--smoke|--regression]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "AI OS - Full Test Suite"
echo "=============================================="
echo "Project Root: $PROJECT_ROOT"
echo "Date: $(date)"
echo "=============================================="

# Parse arguments
ENV="local"
TEST_TYPE="full"
VERBOSE=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --env) ENV="$2"; shift ;;
        --full) TEST_TYPE="full" ;;
        --smoke) TEST_TYPE="smoke" ;;
        --regression) TEST_TYPE="regression" ;;
        --verbose|-v) VERBOSE="--verbose" ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo ""
echo "Configuration:"
echo "  Environment: $ENV"
echo "  Test Type: $TEST_TYPE"
echo "=============================================="

# Track exit codes
BACKEND_EXIT=0
FRONTEND_EXIT=0

# Run backend tests
echo ""
echo "[PHASE 1/2] Backend API Tests"
echo "----------------------------------------------"

cd "$PROJECT_ROOT"

# Check for pytest
if command -v pytest &> /dev/null; then
    if [ "$TEST_TYPE" == "smoke" ]; then
        pytest tests/e2e -m smoke $VERBOSE || BACKEND_EXIT=$?
    elif [ "$TEST_TYPE" == "regression" ]; then
        pytest tests/e2e -m regression $VERBOSE || BACKEND_EXIT=$?
    else
        pytest tests/e2e $VERBOSE || BACKEND_EXIT=$?
    fi
else
    echo "pytest not found, trying with python -m pytest..."
    python -m pytest tests/e2e $VERBOSE || BACKEND_EXIT=$?
fi

echo ""
echo "[PHASE 2/2] Frontend Tests"
echo "----------------------------------------------"

cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Run frontend tests
if [ -f "package.json" ]; then
    npm run test 2>/dev/null || FRONTEND_EXIT=$?
else
    echo "No package.json found in frontend directory"
    FRONTEND_EXIT=1
fi

# Summary
echo ""
echo "=============================================="
echo "TEST SUMMARY"
echo "=============================================="

if [ $BACKEND_EXIT -eq 0 ]; then
    echo "Backend Tests:  ✓ PASSED"
else
    echo "Backend Tests:  ✗ FAILED (exit code: $BACKEND_EXIT)"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    echo "Frontend Tests: ✓ PASSED"
else
    echo "Frontend Tests: ✗ FAILED (exit code: $FRONTEND_EXIT)"
fi

echo "=============================================="

# Exit with failure if any tests failed
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    echo "OVERALL: ✗ SOME TESTS FAILED"
    exit 1
else
    echo "OVERALL: ✓ ALL TESTS PASSED"
    exit 0
fi
