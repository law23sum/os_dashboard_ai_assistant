#!/usr/bin/env python3
"""
Enhanced AI Auto-Fix Script - Cross-Project Version

This enhanced version of ai_auto_fix.py can work across multiple projects
by accepting a --project-root parameter. It integrates with the unified
project orchestrator system.

Usage:
    # Fix a specific project
    python scripts/enhance_ai_autofix.py --project-root /path/to/project

    # Use as fallback for projects without their own ai_auto_fix.py
    python scripts/enhance_ai_autofix.py --project-root /path/to/project --fallback-mode
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the original ai_auto_fix functionality
sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.ai_auto_fix import (
        AutoFixOrchestrator,
        AIFixer,
        ProcessSpec,
        TestSpec,
        main as original_main,
        _build_parser as build_original_parser,
    )
except ImportError as e:
    print(f"❌ Failed to import ai_auto_fix: {e}")
    sys.exit(1)


def enhance_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add cross-project enhancements to the parser."""
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (for cross-project operation)",
    )
    parser.add_argument(
        "--fallback-mode",
        action="store_true",
        help="Run in fallback mode for projects without their own ai_auto_fix.py",
    )
    return parser


def main():
    """Enhanced main function with cross-project support."""
    # Build original parser
    parser = build_original_parser()
    
    # Enhance it
    parser = enhance_parser(parser)
    
    args = parser.parse_args()
    
    # If project-root is specified, change to that directory
    if args.project_root:
        project_root = Path(args.project_root).resolve()
        if not project_root.exists():
            print(f"❌ Project root does not exist: {project_root}")
            return 1
        
        # Change working directory context
        import os
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Adjust paths relative to project root
            if hasattr(args, 'log_dir') and args.log_dir:
                # Convert relative log dirs to absolute
                log_dirs = []
                for log_dir in args.log_dir:
                    log_path = Path(log_dir)
                    if not log_path.is_absolute():
                        log_path = project_root / log_path
                    log_dirs.append(log_path)
                args.log_dir = log_dirs
            
            # Run original main with modified args
            return original_main()
        finally:
            os.chdir(original_cwd)
    else:
        # Run normally
        return original_main()


if __name__ == "__main__":
    sys.exit(main())
