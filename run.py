#!/usr/bin/env python3
"""
Quick launcher for AI OS execution pipeline
This is a convenience wrapper around scripts/execute.py
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Import and run main from execute.py
from execute import main

if __name__ == "__main__":
    sys.exit(main())
