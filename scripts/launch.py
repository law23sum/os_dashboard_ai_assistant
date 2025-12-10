#!/usr/bin/env python3
"""
Launch script for OS Dashboard AI Assistant
Prompts user to choose between web or desktop mode
"""

import sys
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
BACKEND_DIR = REPO_ROOT / "backend_api"

def print_banner():
    print("=" * 60)
    print("  OS Dashboard AI Assistant - Launch Menu")
    print("=" * 60)
    print()

def get_user_choice():
    print("Choose launch mode:")
    print()
    print("  1. Web Browser (http://localhost:5173)")
    print("  2. Desktop App (Electron)")
    print("  3. Backend API Only (http://localhost:8000)")
    print("  4. Both Web and Backend API")
    print("  5. Both Desktop and Backend API")
    print("  0. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (0-5): ").strip()
        if choice in ['0', '1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice. Please enter 0-5.")

def check_dependencies():
    """Check if required dependencies are installed"""
    issues = []
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("Node.js is not installed or not in PATH")
    except FileNotFoundError:
        issues.append("Node.js is not installed")
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("npm is not installed or not in PATH")
    except FileNotFoundError:
        issues.append("npm is not installed")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("Python is not properly installed")
    except FileNotFoundError:
        issues.append("Python is not installed")
    
    return issues

def install_frontend_deps():
    """Install frontend dependencies if needed"""
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("Frontend dependencies not found. Installing...")
        os.chdir(FRONTEND_DIR)
        subprocess.run(['npm', 'install'], check=True)
        os.chdir(REPO_ROOT)
        print("Frontend dependencies installed.")
        return True
    return False

def install_backend_deps():
    """Check and install backend dependencies if needed"""
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("Backend dependencies not found. Installing...")
        requirements = BACKEND_DIR / "requirements.txt"
        if requirements.exists():
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements)
            ], check=True)
            print("Backend dependencies installed.")
            return True
    return False

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting backend API server...")
    os.chdir(BACKEND_DIR)
    return subprocess.Popen([
        sys.executable, 'main.py'
    ], cwd=BACKEND_DIR)

def start_web():
    """Start the web development server"""
    print("Starting web development server...")
    os.chdir(FRONTEND_DIR)
    return subprocess.Popen(['npm', 'run', 'dev:web'], cwd=FRONTEND_DIR)

def start_desktop():
    """Start the desktop app"""
    print("Starting desktop app...")
    os.chdir(FRONTEND_DIR)
    return subprocess.Popen(['npm', 'run', 'dev:desktop'], cwd=FRONTEND_DIR)

def main():
    print_banner()
    
    # Check dependencies
    issues = check_dependencies()
    if issues:
        print("⚠️  Warning: Some dependencies may be missing:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Exiting.")
            return
    
    # Install dependencies if needed
    install_frontend_deps()
    install_backend_deps()
    
    # Get user choice
    choice = get_user_choice()
    
    if choice == '0':
        print("Exiting.")
        return
    
    processes = []
    
    try:
        if choice in ['3', '4', '5']:
            # Start backend
            backend_proc = start_backend()
            processes.append(('Backend API', backend_proc))
            print("Backend API starting at http://localhost:8000")
            print("API docs available at http://localhost:8000/docs")
            print()
        
        if choice in ['1', '4']:
            # Start web
            web_proc = start_web()
            processes.append(('Web Server', web_proc))
            print("Web server starting at http://localhost:5173")
            print()
        
        if choice in ['2', '5']:
            # Start desktop
            desktop_proc = start_desktop()
            processes.append(('Desktop App', desktop_proc))
            print("Desktop app starting...")
            print()
        
        if processes:
            print("=" * 60)
            print("Services started. Press Ctrl+C to stop all services.")
            print("=" * 60)
            print()
            
            # Wait for processes
            try:
                for name, proc in processes:
                    proc.wait()
            except KeyboardInterrupt:
                print("\nShutting down services...")
                for name, proc in processes:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    print(f"  {name} stopped")
                print("All services stopped.")
    
    except Exception as e:
        print(f"Error: {e}")
        # Clean up on error
        for name, proc in processes:
            try:
                proc.terminate()
            except:
                pass

if __name__ == '__main__':
    main()

