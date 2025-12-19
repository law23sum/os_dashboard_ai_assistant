# AI Scripts Documentation

This document describes the two main AI scripts: `cursor_ai.py` and `agents_ai.py`.

## Overview

### cursor_ai.py
A multi-provider AI chat interface that supports 10+ AI providers with automatic API key detection and management.

### agents_ai.py
A multi-agent collaboration system using OpenAI Agents SDK, where agents can work together, analyze codebases, and propose solutions.

## Quick Start

### 1. Install Dependencies

```bash
# For cursor_ai.py (basic chat)
pip install openai anthropic google-genai cohere

# For agents_ai.py (multi-agent system)
pip install openai openai-agents
```

### 2. Set Up API Keys

**Option A: Environment Variables**
```bash
export OPENAI_API_KEY='sk-your-key-here'
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
# ... etc
```

**Option B: .env File**
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key
# ... etc
```

**Get API Keys:**
```bash
python3 cursor_ai.py --get-keys  # Shows all provider links
python3 cursor_ai.py --check-keys  # Check which keys are set
```

See `API_KEYS_ACCESS_GUIDE.md` for detailed instructions.

### 3. Setup Commands (Optional)

```bash
# Make cursor_ai available as command
./setup_cursor_ai.sh

# Make agents_ai available as command
./setup_agents_ai.sh
```

## Usage

### cursor_ai.py - Multi-Provider Chat

**Basic Usage:**
```bash
# Interactive provider selection
python3 cursor_ai.py

# Use specific provider
python3 cursor_ai.py --provider openai

# Use specific model
python3 cursor_ai.py --provider anthropic --model claude-3-5-sonnet-20241022
```

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Opus)
- Google (Gemini 2.5 Flash, Pro)
- xAI (Grok)
- Mistral AI
- Cohere
- Perplexity
- Together AI
- DeepSeek
- Cursor IDE

**Commands in Chat:**
- `/help` - Show help
- `/switch` - Switch provider
- `/clear` - Clear history
- `/exit` - Exit chat
- `/model` - Show current model
- `/providers` - List providers

### agents_ai.py - Multi-Agent System

**Basic Usage:**
```bash
# Interactive agent selection
python3 agents_ai.py

# List available agents
python3 agents_ai.py --list-agents

# Use specific workspace
python3 agents_ai.py --workspace /path/to/workspace

# Use specific agent
python3 agents_ai.py --agent code_analyst
```

**Available Agents:**

1. **code_analyst** - Analyzes codebase structure, finds patterns, documents code
2. **code_writer** - Writes new code, modifies existing code, refactors
3. **solution_architect** - Designs solutions, coordinates agents, reviews code
4. **document_manager** - Manages documents, extracts information, creates docs

**Agent Capabilities:**

All agents can:
- ✅ See their environment (Unix display, shell, user info)
- ✅ Read and write files
- ✅ Execute shell commands (safely sandboxed)
- ✅ Search the web
- ✅ Analyze codebase structure
- ✅ Propose code solutions
- ✅ Communicate with other agents

**Example Workflow:**

```bash
# Start agents system
python3 agents_ai.py

# Ask code_analyst to study the codebase
You: Analyze the codebase structure and identify main components

# Ask code_writer to implement a feature
You: Create a new API endpoint for user authentication

# Agents can collaborate automatically
# The solution_architect coordinates between agents
```

## Features

### cursor_ai.py Features

- ✅ 10+ AI provider support
- ✅ Automatic API key detection from Cursor config
- ✅ Interactive provider selection
- ✅ Conversation history management
- ✅ Model selection per provider
- ✅ API key status checking
- ✅ Direct links to get API keys

### agents_ai.py Features

- ✅ Multi-agent collaboration
- ✅ Codebase analysis tools
- ✅ File manipulation (read/write/list)
- ✅ Shell command execution (sandboxed)
- ✅ Web search integration
- ✅ Inter-agent messaging
- ✅ Environment monitoring
- ✅ Solution proposal system

## Architecture

### cursor_ai.py Architecture

```
cursor_ai.py
├── AIProvider (base class)
├── Provider implementations (OpenAI, Anthropic, etc.)
├── Provider registry
└── Interactive chat loop
```

### agents_ai.py Architecture

```
agents_ai.py
├── AIAgent (individual agent)
├── AgentRegistry (agent coordination)
├── CodebaseAnalyzer (code analysis)
├── FileManager (file operations)
├── EnvironmentMonitor (system info)
└── Agent capabilities system
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Shell Commands**: Agents execute commands in workspace directory only
3. **File Access**: Agents can only access files within workspace
4. **Timeouts**: Commands have 30-second timeout
5. **Sandboxing**: Consider using Docker/containers for production

## Troubleshooting

### cursor_ai.py Issues

**No providers available:**
```bash
python3 cursor_ai.py --check-keys  # Check which keys are set
python3 cursor_ai.py --get-keys     # Get links to obtain keys
```

**Import errors:**
```bash
pip install openai anthropic google-genai cohere
```

### agents_ai.py Issues

**Missing packages:**
```bash
pip install openai openai-agents
```

**API key not set:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
python3 agents_ai.py --check-keys
```

**Agent initialization fails:**
- Check OpenAI API key is valid
- Ensure billing is set up
- Check API rate limits

## Examples

### Example 1: Chat with Claude

```bash
python3 cursor_ai.py --provider anthropic
```

Then in chat:
```
You: Write a Python function to calculate fibonacci numbers
```

### Example 2: Analyze Codebase with Agents

```bash
python3 agents_ai.py --agent code_analyst
```

Then:
```
You: Analyze the project structure and create a summary of all Python modules
```

### Example 3: Multi-Agent Collaboration

```bash
python3 agents_ai.py
```

Then:
```
You: I need to add user authentication. Have the architect design it, 
     the analyst study existing auth patterns, and the writer implement it.
```

## API Key Links Quick Reference

Run `python3 cursor_ai.py --get-keys` for full list, or see `API_KEYS_ACCESS_GUIDE.md`.

**Most Common:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Google: https://aistudio.google.com/app/apikey

## Contributing

When adding new providers to `cursor_ai.py`:
1. Create a new Provider class inheriting from `AIProvider`
2. Add to `PROVIDERS` registry
3. Add to `PROVIDER_DISPLAY_NAMES`
4. Add API key info to `API_KEY_LINKS`

When adding new agents to `agents_ai.py`:
1. Create agent with `AIAgent` class
2. Define role and instructions
3. Set capabilities
4. Register in `AgentRegistry`

## License

See project LICENSE file.

## Support

- Check `API_KEYS_ACCESS_GUIDE.md` for API key issues
- Review script help: `python3 cursor_ai.py --help`
- Review script help: `python3 agents_ai.py --help`
