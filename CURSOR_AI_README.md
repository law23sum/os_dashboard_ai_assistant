# Cursor AI - Multi-Provider Chat Interface

A terminal-based chat interface that allows you to select and chat with different AI providers (OpenAI, Anthropic/Claude, Google/Gemini, xAI/Grok, Cursor IDE).

## Quick Start

### Option 1: Run directly
```bash
python cursor_ai.py
```

### Option 2: Set up as a command (recommended)

Run the setup script:
```bash
./setup_cursor_ai.sh
source ~/.zshrc  # or ~/.bashrc
```

Then you can use:
```bash
cursor_ai
cursor_ai --provider openai
```

### Option 3: Manual alias

Add to your `~/.zshrc` or `~/.bashrc`:
```bash
alias cursor_ai='python3 /path/to/os_dashboard_ai_assistant/cursor_ai.py'
```

## Available Providers

1. **OpenAI** (GPT models)
   - Requires: `OPENAI_API_KEY` environment variable
   - Default model: `gpt-4`
   - Set custom model: `OPENAI_MODEL=gpt-3.5-turbo`

2. **Anthropic** (Claude)
   - Requires: `ANTHROPIC_API_KEY` environment variable
   - Default model: `claude-3-5-sonnet-20241022`
   - Set custom model: `ANTHROPIC_MODEL=claude-3-opus-20240229`

3. **Google** (Gemini)
   - Requires: `GOOGLE_API_KEY` environment variable
   - Default model: `gemini-pro`
   - Set custom model: `GOOGLE_MODEL=gemini-pro-vision`
   - Install: `pip install google-generativeai`

4. **xAI** (Grok)
   - Requires: `XAI_API_KEY` environment variable
   - Default model: `grok-beta`
   - Set custom model: `XAI_MODEL=grok-beta`

5. **Cursor IDE** (Auto-detects from Cursor's config)
   - Automatically detects API keys from Cursor IDE's configuration
   - Uses OpenAI or Anthropic models (whichever is available)
   - Default model: `claude-3-5-sonnet-20241022` (if Anthropic available) or `gpt-4` (if OpenAI available)
   - Set custom model: `CURSOR_MODEL=claude-3-opus-20240229`
   - **No manual setup required!** Automatically finds keys from Cursor's settings

## Usage

### Interactive Mode (Default)

```bash
cursor_ai
```

This will:
1. Show all available providers with their status
2. Let you select a provider
3. Start an interactive chat session

### Pre-select Provider

```bash
cursor_ai --provider openai
cursor_ai --provider anthropic
cursor_ai --provider google
cursor_ai --provider grok
cursor_ai --provider cursor
```

### Specify Model

```bash
cursor_ai --provider openai --model gpt-3.5-turbo
cursor_ai --provider anthropic --model claude-3-opus-20240229
```

### Clear History

```bash
cursor_ai --clear-history
```

## In-Chat Commands

Once in a chat session, you can use these commands:

- `/help` or `/h` - Show help message
- `/switch` or `/s` - Switch to a different AI provider
- `/clear` or `/c` - Clear conversation history
- `/exit` or `/quit` - Exit the chat
- `/model` - Show current model
- `/providers` - List available providers

## Setup API Keys

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export XAI_API_KEY="your-xai-api-key"
```

Or create a `.env` file in the project directory (you may need to load it manually or use `dotenv`).

### Automatic Key Detection (Cursor Provider)

The **Cursor IDE** provider automatically detects API keys from Cursor's configuration files:
- Searches `~/Library/Application Support/Cursor/User/settings.json` (macOS)
- Searches `~/.cursor/settings.json` (Linux)
- Searches `~/.config/cursor/settings.json` (alternative location)
- Also checks `.env` file in project directory

**No manual setup needed!** If you have Cursor IDE installed and configured, the `cursor` provider will automatically use your existing API keys.

## Example Session

```
======================================================================
  Cursor AI - Multi-Provider Chat Interface
======================================================================

Available AI Providers:
----------------------------------------------------------------------
  1) OpenAI (GPT)              ✓
  2) Anthropic (Claude)        ✓
  3) Google (Gemini)           ✗ (API key not set)
  4) xAI (Grok)                ✗ (API key not set)
  5) Cursor IDE                ✓ (auto-detected)
----------------------------------------------------------------------

Select provider (1-4) or name: 1

✓ Selected: OpenAI (GPT)
  Model: gpt-4

Type your message (or /help for commands)
----------------------------------------------------------------------

[OpenAI (GPT)] You: Hello! What can you do?

[OpenAI (GPT)] Thinking...
[OpenAI (GPT)] AI: Hello! I can help you with a wide variety of tasks...

[OpenAI (GPT)] You: /switch

Available AI Providers:
...
```

## Installation Requirements

Install required packages:

```bash
# OpenAI (usually already installed)
pip install openai

# Anthropic
pip install anthropic

# Google Gemini
pip install google-generativeai
```

## Troubleshooting

### "API key not set" error
- Make sure the environment variable is set: `echo $OPENAI_API_KEY`
- Add it to your shell RC file and reload: `source ~/.zshrc`

### "Package not installed" error
- Install the required package: `pip install <package-name>`

### Provider not working
- Check API key is correct
- Verify you have API credits/quota
- Check internet connection
- Try with `--verbose` flag for more details

## Notes

- Conversation history is kept in memory during the session (last 10 exchanges)
- Each provider may have different rate limits and pricing
- Some providers may require additional setup or API approval
- The interface supports multi-turn conversations





