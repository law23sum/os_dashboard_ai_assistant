#!/usr/bin/env python3
"""
Check for Prompttools Updates

This script checks if there's a newer version of Prompttools available
that might support OpenAI 2.x.
"""

import subprocess
import sys
import json
import requests
from packaging import version

def get_installed_version():
    """Get currently installed version of prompttools"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "prompttools"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None

def get_latest_version():
    """Get latest version from PyPI"""
    try:
        response = requests.get("https://pypi.org/pypi/prompttools/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("info", {}).get("version")
    except Exception:
        pass
    return None

def check_openai_compatibility():
    """Check if current prompttools works with OpenAI"""
    try:
        import openai
        import prompttools
        return True, None
    except AttributeError as e:
        if "openai" in str(e).lower() and "error" in str(e).lower():
            return False, "OpenAI 2.x compatibility issue"
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Prompttools Update Checker")
    print("=" * 60)
    print()
    
    # Check installed version
    installed = get_installed_version()
    if installed:
        print(f"✅ Installed version: {installed}")
    else:
        print("❌ Prompttools not installed")
        print("   Install with: pip install prompttools")
        return 1
    
    # Check latest version
    print("\nChecking PyPI for latest version...")
    latest = get_latest_version()
    if latest:
        print(f"✅ Latest version: {latest}")
        
        if installed and version.parse(installed) < version.parse(latest):
            print(f"\n⚠️  Update available: {installed} -> {latest}")
            print("   Update with: pip install --upgrade prompttools")
        else:
            print("\n✅ You have the latest version")
    else:
        print("⚠️  Could not check latest version")
    
    # Check compatibility
    print("\nChecking OpenAI compatibility...")
    compatible, error = check_openai_compatibility()
    if compatible:
        print("✅ Prompttools is compatible with your OpenAI version")
    else:
        print(f"❌ Compatibility issue: {error}")
        print("\nRecommendations:")
        print("  1. Check for updates: pip install --upgrade prompttools")
        print("  2. Monitor: https://github.com/hegelai/prompttools")
        print("  3. The integration will gracefully degrade")
    
    print("\n" + "=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())

