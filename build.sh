#!/bin/bash
"""
Build script for OS Dashboard AI Assistant
Ensures correct working directory before building
"""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "🔨 Building OS Dashboard AI Assistant executable..."
echo "📍 Working directory: $(pwd)"

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Run the build script
"$PYTHON_CMD" build-executable.py
