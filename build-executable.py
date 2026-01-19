#!/usr/bin/env python3
"""
Build executable for AI OS using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Ensure we're running from the correct directory
script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ {cmd}")
        return True
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False

def build_executable():
    """Build executable using PyInstaller"""
    print("🔨 Building AI OS executable...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Check if PyInstaller is available, install if not present
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("⚠️  PyInstaller installation failed, but continuing...")
            # Try to continue anyway in case it's already available
            pass

    # Create spec file for better control
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(SPEC))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Also add parent directory
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

block_cipher = None

a = Analysis(
    ['assistant_hub_gui/main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('assistant_hub_gui/assistant_hub/templates', 'assistant_hub/templates'),
        ('assistant_hub_gui/samples', 'samples'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'ttkbootstrap',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'sqlite3',
        'psutil',
        'openai',
        'anthropic',
        'pandas',
        'numpy',
        'requests',
        'beautifulsoup4',
        'selenium',
        'GitPython',
        'sentence_transformers',
        'sklearn',
        'faiss',
        'cryptography',
        'bcrypt',
        'jwt',
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'alembic',
        'redis',
        'psycopg2',
        'msal',
        'msgraph',
        'google_auth_oauthlib',
        'google_api_python_client',
        'opencv_python',
        'pytesseract',
        'pdfplumber',
        'PyPDF2',
        'docx',
        'icalendar',
        'colorama',
        'structlog',
        'prometheus_client',
        'flask',
        'flask_cors',
        'jinja2',
        'markdown',
        'pygments',
        'celery',
        'apscheduler',
        'click',
        'rich',
        'pydantic',
        'python_dotenv',
        'python_multipart',
        'aiofiles',
        'aiohttp',
        'httpx',
        'joblib',
        'xgboost',
        'statsmodels',
        'spacy',
        'nltk',
        'textblob',
        'google_auth_httplib2',
        'semaphore',
        'icalendar',
        'reportlab',
        'camelo_py',
        'easyocr',
        'torch',
        'transformers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OS_Dashboard_AI_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''

    with open('os_dashboard.spec', 'w') as f:
        f.write(spec_content)

    # Build the executable
    print("🏗️ Building executable...")
    if not run_command("pyinstaller --clean os_dashboard.spec"):
        return False

    # Create distribution directory
    dist_dir = project_root / "dist"
    exe_dir = dist_dir / "OS_Dashboard_AI_Assistant"

    if exe_dir.exists():
        print(f"📦 Executable built successfully in: {exe_dir}")

        # Create a simple installer script
        installer_script = f'''#!/bin/bash
echo "Installing AI OS..."

# Create installation directory
INSTALL_DIR="$HOME/Applications/OS_Dashboard_AI_Assistant"
mkdir -p "$INSTALL_DIR"

# Copy files
cp -r "{exe_dir}"/* "$INSTALL_DIR/"

# Create desktop shortcut (Linux)
DESKTOP_FILE="$HOME/.local/share/applications/os-dashboard.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AI OS
Exec=$INSTALL_DIR/OS_Dashboard_AI_Assistant
Icon=$INSTALL_DIR/icon.png
Type=Application
Categories=Utility;Office;
EOF

chmod +x "$DESKTOP_FILE"
chmod +x "$INSTALL_DIR/OS_Dashboard_AI_Assistant"

echo "✅ Installation complete!"
echo "You can now run the application from:"
echo "  $INSTALL_DIR/OS_Dashboard_AI_Assistant"
echo "Or find it in your applications menu as 'AI OS'"
'''

        installer_path = project_root / "install.sh"
        with open(installer_path, 'w') as f:
            f.write(installer_script)

        os.chmod(installer_path, 0o755)

        print("📦 Created installer script: install.sh")
        print("\n🎉 Build complete!")
        print(f"Executable location: {exe_dir}")
        print(f"Size: {sum(f.stat().st_size for f in exe_dir.rglob('*') if f.is_file()) / (1024*1024):.1f} MB")

        return True
    else:
        print("❌ Build failed - executable not found")
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
