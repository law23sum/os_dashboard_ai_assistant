#!/usr/bin/env python3
"""
Setup script for OS Dashboard AI Assistant
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print a nice banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 OS Dashboard AI Assistant                    ║
║                                                              ║
║  Your intelligent operating system dashboard for task        ║
║  management, document processing, and workflow automation   ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def install_system_dependencies():
    """Install system dependencies based on platform"""
    system = platform.system().lower()

    print(f"📦 Installing system dependencies for {system}...")

    if system == "linux":
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            packages = [
                "tk-dev", "libjpeg-dev", "libpng-dev", "libpoppler-cpp-dev",
                "tesseract-ocr", "libtesseract-dev", "libpq-dev", "libffi-dev",
                "libssl-dev", "git", "postgresql-client", "redis-tools"
            ]
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
            print("✅ System dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install system dependencies")
            print("   Please install them manually:")
            print("   sudo apt-get install tk-dev libjpeg-dev libpng-dev libpoppler-cpp-dev tesseract-ocr libtesseract-dev")
            return False

    elif system == "darwin":  # macOS
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            packages = ["tesseract", "postgresql", "redis"]
            subprocess.run(["brew", "install"] + packages, check=True)
            print("✅ System dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Homebrew not found or installation failed")
            print("   Please install Homebrew: https://brew.sh/")
            return False

    elif system == "windows":
        print("✅ Windows - System dependencies will be handled by pip")
        return True

    else:
        print(f"⚠️  Unknown system: {system}")
        print("   Please install dependencies manually")
        return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")

    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

        # Install from requirements.txt
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def setup_configuration():
    """Set up basic configuration"""
    print("⚙️  Setting up configuration...")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    credentials_dir = config_dir / "credentials"
    credentials_dir.mkdir(exist_ok=True)

    # Create basic config if it doesn't exist
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        basic_config = """
# OS Dashboard AI Assistant Configuration
app:
  name: "OS Dashboard AI Assistant"
  version: "1.0.0"
  environment: "development"

database:
  type: "sqlite"  # Options: sqlite, postgresql
  sqlite_path: "data/app.db"

ai:
  provider: "openai"  # Options: openai, anthropic
  model: "gpt-5-mini"

logging:
  level: "INFO"
  file: "logs/app.log"

integrations:
  microsoft_graph:
    enabled: false
  google_workspace:
    enabled: false
  git:
    enabled: true
"""
        config_file.write_text(basic_config)
        print("✅ Basic configuration created")

    # Create data and logs directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    print("✅ Configuration setup complete")

def create_desktop_shortcut():
    """Create desktop shortcut"""
    system = platform.system().lower()

    if system == "linux":
        desktop_file = Path.home() / ".local/share/applications/os-dashboard.desktop"
        desktop_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""[Desktop Entry]
Name=OS Dashboard AI Assistant
Exec={Path.cwd() / "start_ui.py"}
Icon={Path.cwd() / "icon.png"}
Type=Application
Categories=Utility;Office;
Terminal=false
"""

        desktop_file.write_text(content)
        desktop_file.chmod(0o755)
        print("✅ Desktop shortcut created")

    elif system == "darwin":  # macOS
        # Create alias on Desktop
        desktop_path = Path.home() / "Desktop"
        app_path = Path.cwd() / "start_ui.py"

        if desktop_path.exists():
            try:
                subprocess.run(["osascript", "-e", f'tell application "Finder" to make alias file to POSIX file "{app_path}" at POSIX file "{desktop_path}"'], check=True)
                print("✅ Desktop alias created")
            except subprocess.CalledProcessError:
                print("⚠️  Could not create desktop alias")

def create_run_script():
    """Create a simple run script that forwards to start_ui.py."""
    run_script = """#!/usr/bin/env python3
\"\"\"Backward-compatible shim that routes to start_ui.py\"\"\"
from start_ui import main as start_main

if __name__ == "__main__":
    raise SystemExit(start_main())
"""

    run_file = Path("run.py")
    run_file.write_text(run_script)
    run_file.chmod(0o755)
    print("✅ Compatibility launcher created: run.py → start_ui.py")

def main():
    """Main setup function"""
    print_banner()

    print("🔧 Starting OS Dashboard AI Assistant setup...\\n")

    # Check Python version
    if not check_python_version():
        return False

    # Install system dependencies
    if not install_system_dependencies():
        return False

    # Install Python dependencies
    if not install_python_dependencies():
        return False

    # Setup configuration
    setup_configuration()

    # Create run script
    create_run_script()

    # Create desktop shortcut
    create_desktop_shortcut()

    print("\\n🎉 Setup complete!")
    print("\\n🚀 To start the application:")
    print("   python start_ui.py")
    print("   # or double-click start_ui.py")
    print("\\n📚 For help, visit: https://github.com/yourusername/os-dashboard-ai-assistant")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
