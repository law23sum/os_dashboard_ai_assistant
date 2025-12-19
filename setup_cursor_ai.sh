#!/bin/bash
# Setup script to make cursor_ai and agents_ai available as commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_AI_SCRIPT="$SCRIPT_DIR/cursor_ai.py"
AGENTS_AI_SCRIPT="$SCRIPT_DIR/agents_ai.py"

# Detect shell
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "bash" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Create aliases
ALIAS_CURSOR="alias cursor_ai='python3 \"$CURSOR_AI_SCRIPT\"'"
ALIAS_AGENTS="alias agents_ai='python3 \"$AGENTS_AI_SCRIPT\"'"

# Check if aliases already exist
if grep -q "alias cursor_ai=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  cursor_ai alias already exists in $SHELL_RC"
else
    echo "" >> "$SHELL_RC"
    echo "# Cursor AI commands" >> "$SHELL_RC"
    echo "$ALIAS_CURSOR" >> "$SHELL_RC"
    echo "✓ Added cursor_ai alias to $SHELL_RC"
fi

if grep -q "alias agents_ai=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  agents_ai alias already exists in $SHELL_RC"
else
    echo "$ALIAS_AGENTS" >> "$SHELL_RC"
    echo "✓ Added agents_ai alias to $SHELL_RC"
fi

echo ""
echo "Please run: source $SHELL_RC"
echo "Or open a new terminal."

# Alternatively, create symlinks in a local bin directory
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

if [ -d "$LOCAL_BIN" ] && [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    echo "💡 Tip: Add $LOCAL_BIN to your PATH for easier access:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $SHELL_RC"
fi

# Create wrapper script for cursor_ai
WRAPPER_SCRIPT_CURSOR="$LOCAL_BIN/cursor_ai"
cat > "$WRAPPER_SCRIPT_CURSOR" << 'EOF'
#!/bin/bash
# Wrapper script for cursor_ai
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$SCRIPT_DIR/cursor_ai.py" "$@"
EOF
chmod +x "$WRAPPER_SCRIPT_CURSOR"
echo "✓ Created wrapper script at $WRAPPER_SCRIPT_CURSOR"

# Create wrapper script for agents_ai
WRAPPER_SCRIPT_AGENTS="$LOCAL_BIN/agents_ai"
cat > "$WRAPPER_SCRIPT_AGENTS" << 'EOF'
#!/bin/bash
# Wrapper script for agents_ai
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$SCRIPT_DIR/agents_ai.py" "$@"
EOF
chmod +x "$WRAPPER_SCRIPT_AGENTS"
echo "✓ Created wrapper script at $WRAPPER_SCRIPT_AGENTS"

echo ""
echo "Setup complete! You can now use:"
echo "  cursor_ai              # Interactive provider selection"
echo "  agents_ai              # Run the Multi-Agent System (AIC, Aria, Sora)"


