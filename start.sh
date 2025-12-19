#!/bin/bash
# Simple startup script for OS Dashboard AI Assistant

set -e

echo "=================================="
echo "OS Dashboard AI Assistant Launcher"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using: $PYTHON_CMD"
echo ""

# Check for command line argument
MODE="${1:-browser}"

echo "Starting in $MODE mode..."
echo ""

# Run the unified launcher
$PYTHON_CMD unified_launcher.py --mode "$MODE"
