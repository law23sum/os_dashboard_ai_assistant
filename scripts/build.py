#!/usr/bin/env python3
"""
Build script for AI OS
Builds for web, desktop, or all platforms
"""

import sys
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"

def print_banner():
    print("=" * 60)
    print("  AI OS - Build Script")
    print("=" * 60)
    print()

def get_build_choice():
    print("Choose build target:")
    print()
    print("  1. Web (static files)")
    print("  2. Desktop - Windows")
    print("  3. Desktop - macOS")
    print("  4. Desktop - Linux")
    print("  5. Desktop - All Platforms")
    print("  6. Web + All Desktop Platforms")
    print("  0. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (0-6): ").strip()
        if choice in ['0', '1', '2', '3', '4', '5', '6']:
            return choice
        print("Invalid choice. Please enter 0-6.")

def build_web():
    """Build web version"""
    print("Building web version...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'run', 'build:web'], check=True)
    print("✓ Web build complete: frontend/dist/")
    return True

def build_desktop_win():
    """Build Windows desktop app"""
    print("Building Windows desktop app...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'run', 'build:desktop:win'], check=True)
    print("✓ Windows build complete: frontend/dist-electron/")
    return True

def build_desktop_mac():
    """Build macOS desktop app"""
    print("Building macOS desktop app...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'run', 'build:desktop:mac'], check=True)
    print("✓ macOS build complete: frontend/dist-electron/")
    return True

def build_desktop_linux():
    """Build Linux desktop app"""
    print("Building Linux desktop app...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'run', 'build:desktop:linux'], check=True)
    print("✓ Linux build complete: frontend/dist-electron/")
    return True

def build_desktop_all():
    """Build desktop app for all platforms"""
    print("Building desktop app for all platforms...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'run', 'build:desktop:all'], check=True)
    print("✓ All platforms build complete: frontend/dist-electron/")
    return True

def main():
    print_banner()
    
    # Check if in frontend directory
    if not (FRONTEND_DIR / "package.json").exists():
        print(f"Error: Frontend directory not found at {FRONTEND_DIR}")
        return
    
    # Check Node.js and npm
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: Node.js and npm are required for building")
        return
    
    # Install dependencies
    print("Installing dependencies...")
    os.chdir(FRONTEND_DIR)
    subprocess.run(['npm', 'install'], check=True)
    os.chdir(REPO_ROOT)
    print("Dependencies installed.\n")
    
    # Get build choice
    choice = get_build_choice()
    
    if choice == '0':
        print("Exiting.")
        return
    
    try:
        if choice == '1':
            build_web()
        elif choice == '2':
            build_web()
            build_desktop_win()
        elif choice == '3':
            build_web()
            build_desktop_mac()
        elif choice == '4':
            build_web()
            build_desktop_linux()
        elif choice == '5':
            build_web()
            build_desktop_all()
        elif choice == '6':
            build_web()
            build_desktop_all()
        
        print()
        print("=" * 60)
        print("Build complete!")
        print("=" * 60)
    
    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBuild cancelled.")
        sys.exit(1)

if __name__ == '__main__':
    main()

