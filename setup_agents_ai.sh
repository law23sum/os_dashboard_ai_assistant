#!/bin/bash
# Setup script to make agents_ai available as a command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_AI_SCRIPT="$SCRIPT_DIR/agents_ai.py"

# Make the script executable
chmod +x "$AGENTS_AI_SCRIPT"

# Detect shell
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "bash" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Create alias
ALIAS_LINE="alias agents_ai='python3 \"$AGENTS_AI_SCRIPT\"'"

# Check if alias already exists
if grep -q "alias agents_ai=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  agents_ai alias already exists in $SHELL_RC"
    echo "   You may want to update it manually."
else
    echo "" >> "$SHELL_RC"
    echo "# Multi-Agent AI System command" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "✓ Added agents_ai alias to $SHELL_RC"
    echo ""
    echo "Please run: source $SHELL_RC"
    echo "Or open a new terminal and type: agents_ai"
fi

# Alternatively, create a symlink in a local bin directory
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

if [ -d "$LOCAL_BIN" ] && [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    echo "💡 Tip: Add $LOCAL_BIN to your PATH for easier access:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $SHELL_RC"
fi

# Create wrapper script in local bin
WRAPPER_SCRIPT="$LOCAL_BIN/agents_ai"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Wrapper script for agents_ai
SCRIPT_DIR="$SCRIPT_DIR"
exec python3 "\$SCRIPT_DIR/agents_ai.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo "✓ Created wrapper script at $WRAPPER_SCRIPT"

echo ""
echo "Setup complete! You can now use:"
echo "  agents_ai                          # Interactive mode"
echo "  agents_ai --analyze                # Analyze codebase"
echo "  agents_ai --collaborate 'task'     # Collaborative task"
echo "  agents_ai --propose 'problem'      # Propose solution"
echo "  agents_ai --check-display          # Check display access"
echo "  agents_ai --help                   # Show help"
echo ""
echo "📚 See AGENTS_AI_GUIDE.md for detailed documentation"
