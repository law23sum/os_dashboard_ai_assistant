#!/bin/bash
# Setup script to make cursor_ai available as a command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_AI_SCRIPT="$SCRIPT_DIR/cursor_ai.py"

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
ALIAS_LINE="alias cursor_ai='python3 \"$CURSOR_AI_SCRIPT\"'"

# Check if alias already exists
if grep -q "alias cursor_ai=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  cursor_ai alias already exists in $SHELL_RC"
    echo "   You may want to update it manually."
else
    echo "" >> "$SHELL_RC"
    echo "# Cursor AI command" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "✓ Added cursor_ai alias to $SHELL_RC"
    echo ""
    echo "Please run: source $SHELL_RC"
    echo "Or open a new terminal and type: cursor_ai"
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
WRAPPER_SCRIPT="$LOCAL_BIN/cursor_ai"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# Wrapper script for cursor_ai
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$SCRIPT_DIR/cursor_ai.py" "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo "✓ Created wrapper script at $WRAPPER_SCRIPT"

echo ""
echo "Setup complete! You can now use:"
echo "  cursor_ai              # Interactive provider selection"
echo "  cursor_ai --provider openai"
echo "  cursor_ai --help"





