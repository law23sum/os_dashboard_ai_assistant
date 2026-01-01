#!/bin/bash
# Setup script to make agents_ai, ai_agent, and persona shims available as commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_AI_SCRIPT="$SCRIPT_DIR/agents_ai.py"
AI_AGENT_SCRIPT="$SCRIPT_DIR/ai_agent"
AIC_SCRIPT="$SCRIPT_DIR/AIC"
ARIA_SCRIPT="$SCRIPT_DIR/Aria"
SORA_SCRIPT="$SCRIPT_DIR/Sora"
CHATGPT_SCRIPT="$SCRIPT_DIR/ChatGPT"

chmod +x "$AGENTS_AI_SCRIPT" 2>/dev/null
chmod +x "$AI_AGENT_SCRIPT" 2>/dev/null
chmod +x "$AIC_SCRIPT" 2>/dev/null
chmod +x "$ARIA_SCRIPT" 2>/dev/null
chmod +x "$SORA_SCRIPT" 2>/dev/null
chmod +x "$CHATGPT_SCRIPT" 2>/dev/null

# Detect shell
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "bash" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

append_alias() {
    local alias_line="$1"
    local alias_name="$2"
    if grep -q "alias ${alias_name}=" "$SHELL_RC" 2>/dev/null; then
        echo "WARN: ${alias_name} alias already exists in $SHELL_RC"
        echo "      You may want to update it manually."
    else
        echo "" >> "$SHELL_RC"
        echo "# AI agent command: ${alias_name}" >> "$SHELL_RC"
        echo "$alias_line" >> "$SHELL_RC"
        echo "OK: Added ${alias_name} alias to $SHELL_RC"
    fi
}

if [ -f "$AGENTS_AI_SCRIPT" ]; then
    append_alias "alias agents_ai='python3 \"$AGENTS_AI_SCRIPT\"'" "agents_ai"
fi
if [ -f "$AI_AGENT_SCRIPT" ]; then
    append_alias "alias ai_agent='\"$AI_AGENT_SCRIPT\"'" "ai_agent"
fi
if [ -f "$AIC_SCRIPT" ]; then
    append_alias "alias AIC='\"$AIC_SCRIPT\"'" "AIC"
fi
if [ -f "$ARIA_SCRIPT" ]; then
    append_alias "alias Aria='\"$ARIA_SCRIPT\"'" "Aria"
fi
if [ -f "$SORA_SCRIPT" ]; then
    append_alias "alias Sora='\"$SORA_SCRIPT\"'" "Sora"
fi
if [ -f "$CHATGPT_SCRIPT" ]; then
    append_alias "alias ChatGPT='\"$CHATGPT_SCRIPT\"'" "ChatGPT"
fi

LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

write_exec_wrapper() {
    local name="$1"
    local target="$2"
    local wrapper="$LOCAL_BIN/$name"
    cat > "$wrapper" << WRAP
#!/bin/bash
exec "$target" "\$@"
WRAP
    chmod +x "$wrapper"
    echo "OK: Created wrapper script at $wrapper"
}

if [ -d "$LOCAL_BIN" ] && [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    echo "TIP: Add $LOCAL_BIN to your PATH for easier access:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $SHELL_RC"
fi

if [ -f "$AGENTS_AI_SCRIPT" ]; then
    write_exec_wrapper "agents_ai" "$AGENTS_AI_SCRIPT"
fi
if [ -f "$AI_AGENT_SCRIPT" ]; then
    write_exec_wrapper "ai_agent" "$AI_AGENT_SCRIPT"
fi
if [ -f "$AIC_SCRIPT" ]; then
    write_exec_wrapper "AIC" "$AIC_SCRIPT"
fi
if [ -f "$ARIA_SCRIPT" ]; then
    write_exec_wrapper "Aria" "$ARIA_SCRIPT"
fi
if [ -f "$SORA_SCRIPT" ]; then
    write_exec_wrapper "Sora" "$SORA_SCRIPT"
fi
if [ -f "$CHATGPT_SCRIPT" ]; then
    write_exec_wrapper "ChatGPT" "$CHATGPT_SCRIPT"
fi

echo ""
echo "Setup complete! You can now use:"
echo "  agents_ai                          # Multi-agent system (AIC, Aria, Sora)"
echo "  ai_agent                           # Unified agent interface"
echo "  AIC                                # Direct AIC call"
echo "  Aria                               # Direct Aria call"
echo "  Sora                               # Direct Sora call"
echo "  ChatGPT                            # Auto-route to AIC/Sora/Aria"
echo ""
echo "Please run: source $SHELL_RC"

# Check for required packages
if command -v python3 >/dev/null 2>&1; then
    echo ""
    echo "Checking required packages..."
    if python3 -c "import openai" 2>/dev/null; then
        echo "OK: openai package installed"
    else
        echo "WARN: openai package not installed. Install with: pip install openai"
    fi

    if python3 -c "import openai_agents" 2>/dev/null; then
        echo "OK: openai-agents package installed"
    else
        echo "WARN: openai-agents package not installed. Install with: pip install openai-agents"
    fi
fi
