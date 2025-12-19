#!/bin/bash
# Run Frontend E2E Tests
# Usage: ./scripts/run_frontend_tests.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=============================================="
echo "Frontend E2E Test Runner"
echo "=============================================="

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[1/3] Installing dependencies..."
    npm install
else
    echo "[1/3] Dependencies already installed."
fi

# Run tests based on arguments
if [ "$1" == "--coverage" ]; then
    echo "[2/3] Running tests with coverage..."
    npm run test:coverage
elif [ "$1" == "--watch" ]; then
    echo "[2/3] Running tests in watch mode..."
    npm run test:watch
else
    echo "[2/3] Running tests..."
    npm run test
fi

echo "[3/3] Tests completed."
echo "=============================================="
