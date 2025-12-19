#!/bin/bash
# Setup script for Unified Project Orchestrator System
# This script sets up the complete unified system for managing all Git projects

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$REPO_ROOT/scripts"

echo "🚀 Setting up Unified Project Orchestrator System..."
echo ""

# Make scripts executable
echo "📝 Making scripts executable..."
chmod +x "$SCRIPTS_DIR/unified_project_orchestrator.py"
chmod +x "$SCRIPTS_DIR/unified_terminal_shell.py"
chmod +x "$SCRIPTS_DIR/ai_auto_fix.py"
chmod +x "$SCRIPTS_DIR/project_autofix_orchestrator.py"
chmod +x "$SCRIPTS_DIR/workspace_auto_guard.py"
chmod +x "$SCRIPTS_DIR/workspace_autofix_shell.py"

echo "✅ Scripts are now executable"
echo ""

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip3 install -r "$REPO_ROOT/backend_api/requirements.txt" || {
        echo "❌ Failed to install dependencies"
        exit 1
    }
fi

echo "✅ Dependencies checked"
echo ""

# Create symlinks for easy access
echo "🔗 Creating symlinks..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

ln -sf "$SCRIPTS_DIR/unified_project_orchestrator.py" "$BIN_DIR/osdash-orchestrator"
ln -sf "$SCRIPTS_DIR/unified_terminal_shell.py" "$BIN_DIR/osdash-shell"
ln -sf "$SCRIPTS_DIR/ai_auto_fix.py" "$BIN_DIR/osdash-autofix"

echo "✅ Symlinks created in $BIN_DIR"
echo ""

# Test discovery
echo "🧪 Testing project discovery..."
python3 "$SCRIPTS_DIR/unified_project_orchestrator.py" --max-depth 3 || {
    echo "⚠️  Project discovery test had issues (this is okay if no projects found)"
}

echo ""
echo "✨ Setup complete!"
echo ""
echo "Usage:"
echo "  osdash-orchestrator --help          # Unified project orchestrator"
echo "  osdash-shell                        # Interactive terminal shell"
echo "  osdash-autofix --help               # Auto-fix script"
echo ""
echo "Or use directly:"
echo "  python3 scripts/unified_project_orchestrator.py"
echo "  python3 scripts/unified_terminal_shell.py"
echo ""
