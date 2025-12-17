# Interactive Terminal Chat with AI Agents

This project now includes an interactive terminal chat interface that allows you to select and chat with different AI agents.

## Quick Start

### Option 1: Using the standalone script

```bash
python cursor_chat.py
```

### Option 2: Using the CLI command

```bash
python -m ui.terminal.cli chat
```

Or if you have `osdash` installed:

```bash
osdash chat
```

## Features

- **Interactive AI Selection**: Choose from 4 AI agents:
  - **AIC**: Deep reasoning / agentic control (gpt-5.2-pro)
  - **Aria**: Coding + content polish (gpt-5.1-codex-max)
  - **Sora**: Complex reasoning + planning (gpt-5.2)
  - **Chris**: Cost-optimized default chat (gpt-5-mini)

- **Interactive Commands**:
  - `/help` or `/h` - Show help message
  - `/switch` or `/s` - Switch to a different AI agent
  - `/clear` or `/c` - Clear conversation history
  - `/exit` or `/quit` - Exit the chat
  - `/model` - Show current AI model

- **Conversation History**: Your conversations are saved to the database and persist across sessions

- **Shell Command Support**: AI agents can execute shell commands (can be disabled with `--no-shell`)

## Command Line Options

```bash
python cursor_chat.py --help
```

Available options:
- `--agent AIC|Aria|Sora|Chris` - Pre-select an AI agent (skips interactive selection)
- `--clear-history` - Start with empty conversation history
- `--clear-on-switch` - Clear history when switching agents
- `--enable-shell` - Allow AI to execute shell commands (default: True)
- `--no-shell` - Disable shell command execution
- `--verbose` or `-v` - Show verbose error messages

## Examples

### Start with a specific agent

```bash
python cursor_chat.py --agent Aria
```

### Start with empty history

```bash
python cursor_chat.py --clear-history
```

### Disable shell commands

```bash
python cursor_chat.py --no-shell
```

## Usage Example

```
======================================================================
  OS Dashboard AI Assistant - Interactive Terminal Chat
======================================================================

Available AI Agents:
----------------------------------------------------------------------
  1) AIC       - Deep reasoning / agentic control (gpt-5.2-pro)
  2) Aria      - Coding + content polish (gpt-5.1-codex-max)
  3) Sora      - Complex reasoning + planning (gpt-5.2)
  4) Chris     - Cost-optimized default chat (gpt-5-mini)
----------------------------------------------------------------------

Select AI agent (1-4) or name: 2

✓ Selected AI: Aria
  Model: gpt-5.1-codex-max

Type your message (or /help for commands)
----------------------------------------------------------------------

[Aria] You: Hello! Can you help me with Python?

[Aria] Thinking...
[Aria] AI: Hello! I'd be happy to help you with Python. What would you like to know or work on?

[Aria] You: /switch

Available AI Agents:
...
```

## Notes

- The chat interface uses readline for better input handling on Unix systems
- All conversations are saved to the database and can be viewed with the `history` command
- Press Ctrl+C or type `/exit` to quit
- The AI agents have access to shell commands by default (use `--no-shell` to disable)





