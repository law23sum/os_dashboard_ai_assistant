#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Try to run the GUI application
try:
    from assistant_hub_gui.main import main
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run the bootstrap script first: python tools/bootstrap.py")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n👋 Goodbye!")
    sys.exit(0)
