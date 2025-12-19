# AI Systems - Complete Setup Guide

This document provides an overview of the AI systems available in this project, including the updated cursor_ai chat interface and the new multi-agent agents_ai system.

## 📚 Quick Links

- **[API Keys Guide](API_KEYS_GUIDE.md)** - Links to obtain all AI API keys
- **[Agents AI Guide](AGENTS_AI_GUIDE.md)** - Detailed documentation for the multi-agent system
- **[.env.example](.env.example)** - Complete environment configuration template

---

## 🎯 Overview

This project now includes two powerful AI systems:

### 1. cursor_ai - Multi-Provider Chat Interface

A terminal-based chat interface supporting 10+ AI providers with automatic API key detection.

**Supported Providers:**
- OpenAI (GPT-4, GPT-4 Turbo, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- Google (Gemini 2.0 Flash, Gemini 1.5 Pro)
- xAI (Grok)
- Perplexity AI
- Cohere
- Mistral AI
- DeepSeek
- Groq (Fast Inference)
- Cursor IDE (uses OpenAI/Anthropic)

### 2. agents_ai - Multi-Agent Collaboration System

A sophisticated multi-agent system where specialized AI agents collaborate on complex tasks.

**Agents:**
- **AIC** (Chief) - Applied systems, operations, integration
- **Aria** (Doctor) - Philosophy, meaning, institutions
- **Sora** (Doctor) - Formal structure, law, economics

**Capabilities:**
- Unix display interaction
- File manipulation
- Code analysis and generation
- Inter-agent communication
- Collaborative problem solving
- Code proposal and review

---

## 🚀 Quick Start

### Step 1: Get API Keys

Get your OpenAI API key (required for both systems):

```bash
# Visit: https://platform.openai.com/api-keys
```

For other providers, see **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** for direct links.

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor

# At minimum, add:
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install openai anthropic google-genai cohere

# Optional: For display interaction
sudo apt-get install xdotool  # Ubuntu/Debian
brew install xdotool           # macOS
```

### Step 4: Setup Commands

```bash
# Setup cursor_ai
bash setup_cursor_ai.sh

# Setup agents_ai
bash setup_agents_ai.sh

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

---

## 💬 Using cursor_ai

### Interactive Chat

```bash
# Start cursor_ai and select a provider
cursor_ai

# Or specify provider directly
cursor_ai --provider openai
cursor_ai --provider anthropic
cursor_ai --provider google
```

### Check Available Providers

```bash
# Check which API keys are configured
cursor_ai --check-keys

# Get links to obtain API keys
cursor_ai --get-keys
```

### Example Session

```bash
$ cursor_ai --provider anthropic

======================================================================
  Cursor AI - Multi-Provider Chat Interface
======================================================================

✓ Selected: Anthropic (Claude)
  Model: claude-3-5-sonnet-20241022

Type your message (or /help for commands)
----------------------------------------------------------------------

[Anthropic (Claude)] You: Explain quantum computing in simple terms

[Anthropic (Claude)] AI: Quantum computing is like having a computer 
that can explore multiple solutions simultaneously...

[Anthropic (Claude)] You: /switch

Available AI Providers:
----------------------------------------------------------------------
  1) OpenAI (GPT)              ✓
  2) Anthropic (Claude)        ✓
  3) Google (Gemini)           ✓
  ...

[Anthropic (Claude)] You: /exit

Goodbye! 👋
```

---

## 🤖 Using agents_ai

### Interactive Mode

```bash
# Start the multi-agent system
agents_ai

# Use commands
[agents_ai] > analyze
[agents_ai] > collaborate Improve authentication system
[agents_ai] > propose Add real-time monitoring
[agents_ai] > ask AIC How to optimize database queries?
[agents_ai] > exit
```

### Command Line Mode

```bash
# Analyze codebase with all agents
agents_ai --analyze

# Collaborative task
agents_ai --collaborate "Design a plugin architecture"

# Propose solution
agents_ai --propose "How to implement caching?"

# Check display access
agents_ai --check-display

# Save session
agents_ai --analyze --save-session analysis.json
```

### Example Workflow

```bash
# 1. Ask AIC for technical analysis
agents_ai
[agents_ai] > ask AIC Analyze our current authentication system

AIC: From an operational standpoint, the current authentication 
system uses session-based auth. Here are my recommendations:
1. Implement JWT tokens for stateless authentication
2. Add rate limiting to prevent brute force attacks
3. Use bcrypt for password hashing
4. Implement refresh token rotation
...

# 2. Get ethical perspective from Aria
[agents_ai] > ask Aria What are the ethical implications of storing user data?

Aria: From a philosophical perspective, user data storage requires
careful consideration of several principles:
1. Consent - Users must explicitly agree to data collection
2. Transparency - Clear communication about what data is stored
3. Purpose Limitation - Data should only be used for stated purposes
...

# 3. Get formal validation from Sora
[agents_ai] > ask Sora What legal requirements apply to user authentication?

Sora: From a legal and formal standpoint, authentication systems
must comply with:
1. GDPR requirements for EU users
2. CCPA for California residents
3. Password security standards (NIST guidelines)
...

# 4. Have all agents collaborate
[agents_ai] > collaborate Design a comprehensive authentication system

==================================================================
  Collaborative Task: Design a comprehensive authentication system
==================================================================

💭 AIC analyzing task...
💭 Aria analyzing task...
💭 Sora analyzing task...

[Detailed analysis from each agent's perspective]

==================================================================
  Inter-Agent Discussion
==================================================================

📨 Messages exchanged between agents...
```

---

## 📖 Documentation

### Complete Guides

1. **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)**
   - Direct links to get API keys for 30+ services
   - Setup instructions for each provider
   - Pricing and documentation links
   - Environment variable reference

2. **[AGENTS_AI_GUIDE.md](AGENTS_AI_GUIDE.md)**
   - Complete multi-agent system documentation
   - Agent roles and capabilities
   - Architecture diagrams
   - Advanced usage examples
   - API reference

3. **[.env.example](.env.example)**
   - Complete environment variable template
   - All supported API keys
   - Configuration options
   - Comments and examples

---

## 🔑 API Keys Quick Reference

### Essential Keys

```bash
# OpenAI (Required for both systems)
OPENAI_API_KEY=sk-your-key
# Get: https://platform.openai.com/api-keys

# Anthropic Claude (Recommended)
ANTHROPIC_API_KEY=sk-ant-your-key
# Get: https://console.anthropic.com/settings/keys

# Google Gemini (Recommended)
GOOGLE_API_KEY=your-google-key
# Get: https://aistudio.google.com/app/apikey
```

### Additional Providers

See **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** for complete list including:
- xAI (Grok)
- Perplexity AI
- Cohere
- Mistral AI
- DeepSeek
- Groq
- And 20+ more services

---

## 🎨 Features

### cursor_ai Features

✅ **10+ AI Providers** - OpenAI, Anthropic, Google, xAI, Perplexity, Cohere, Mistral, DeepSeek, Groq, Cursor  
✅ **Interactive Chat** - Terminal-based conversational interface  
✅ **Provider Switching** - Switch between providers mid-conversation  
✅ **Auto-Detection** - Automatically detect API keys from environment  
✅ **Conversation History** - Maintains context across messages  
✅ **Easy Setup** - One command to set up shell alias  

### agents_ai Features

✅ **Multi-Agent Collaboration** - Three specialized agents work together  
✅ **Role-Based Specialization** - Each agent has unique expertise  
✅ **Unix Display Interaction** - Agents can see and interact with display  
✅ **File Manipulation** - Read, write, and analyze files  
✅ **Code Analysis** - Comprehensive codebase analysis  
✅ **Code Generation** - Propose and review code changes  
✅ **Inter-Agent Communication** - Agents discuss and collaborate  
✅ **Session Management** - Save and load collaboration sessions  

---

## 🏗️ Architecture

### cursor_ai Architecture

```
┌─────────────────────────────────────────────────────┐
│                   cursor_ai.py                       │
│  ┌────────────────────────────────────────────┐    │
│  │          Provider Registry                  │    │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │    │
│  │  │OpenAI│  │Claude│  │Gemini│  │ Grok │  │    │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  │    │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │    │
│  │  │Perplex│ │Cohere│  │Mistral│ │DeepSk│  │    │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  │    │
│  └────────────────────────────────────────────┘    │
│                      │                               │
│                      ▼                               │
│            Interactive Chat Loop                     │
└─────────────────────────────────────────────────────┘
```

### agents_ai Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AgentSystem                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Message Router & Coordinator            │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                  │                  │             │
│    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐       │
│    │   AIC   │◄─────►│  Aria   │◄─────►│  Sora   │       │
│    │ (Chief) │       │(Doctor) │       │(Doctor) │       │
│    │         │       │         │       │         │       │
│    │ Applied │       │ Meaning │       │ Formal  │       │
│    │ Systems │       │  Value  │       │ Structure│      │
│    └────┬────┘       └────┬────┘       └────┬────┘       │
│         │                  │                  │             │
│         └──────────┬───────┴─────────┬────────┘            │
│                    │                 │                      │
│              ┌─────▼─────┐     ┌────▼─────┐               │
│              │  ChatGPT  │     │   Unix   │               │
│              │    API    │     │  System  │               │
│              └───────────┘     └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Issue: "No API key found"

```bash
# Check if key is set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY='sk-your-key-here'

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Issue: "Package not installed"

```bash
# Install missing packages
pip install openai anthropic google-genai cohere

# Or install all at once
pip install -r requirements.txt
```

### Issue: "Command not found: cursor_ai"

```bash
# Re-run setup
bash setup_cursor_ai.sh

# Reload shell
source ~/.zshrc  # or ~/.bashrc

# Or use full path
python3 /path/to/cursor_ai.py
```

### Issue: "Display not accessible" (agents_ai)

```bash
# Set DISPLAY variable
export DISPLAY=:0

# Install xdotool (optional, for display interaction)
sudo apt-get install xdotool
```

---

## 📊 Comparison: cursor_ai vs agents_ai

| Feature                    | cursor_ai | agents_ai |
|---------------------------|-----------|-----------|
| **Purpose**               | Chat with AI | Multi-agent collaboration |
| **Providers**             | 10+ | 1 (OpenAI/ChatGPT) |
| **Agents**                | 1 | 3 (AIC, Aria, Sora) |
| **Code Analysis**         | ❌ | ✅ |
| **File Manipulation**     | ❌ | ✅ |
| **Inter-agent Comm**      | ❌ | ✅ |
| **Display Interaction**   | ❌ | ✅ |
| **Conversation History**  | ✅ | ✅ |
| **Session Saving**        | ❌ | ✅ |
| **Best For**              | Quick questions, experiments | Complex tasks, code review, architecture |

---

## 🎯 Use Cases

### cursor_ai Use Cases

1. **Quick Questions** - Ask any AI provider a quick question
2. **Compare Providers** - Test same prompt across different AI models
3. **Research** - Deep dive into topics with different AI perspectives
4. **Writing** - Generate content with various AI styles
5. **Experiments** - Try new AI models without changing code

### agents_ai Use Cases

1. **Code Review** - Have multiple perspectives review code
2. **Architecture Design** - Collaborate on system design
3. **Problem Solving** - Complex problems requiring multiple viewpoints
4. **Refactoring** - Analyze and propose improvements
5. **Documentation** - Generate comprehensive documentation
6. **Testing Strategy** - Design test plans with multiple considerations
7. **Security Audit** - Review from operational, ethical, and legal angles

---

## 📝 Examples

### Example 1: Using cursor_ai for Quick Question

```bash
$ cursor_ai --provider google

[Google (Gemini)] You: What's the difference between REST and GraphQL?

[Google (Gemini)] AI: REST and GraphQL are both API design patterns:

REST (Representational State Transfer):
- Multiple endpoints for different resources
- Fixed data structure returned
- Uses standard HTTP methods (GET, POST, PUT, DELETE)
- Easier to cache
- Well-established with many tools

GraphQL:
- Single endpoint for all queries
- Client specifies exactly what data needed
- Reduces over-fetching and under-fetching
- Strongly typed schema
- Real-time subscriptions built-in

Choose REST for:
- Simple, resource-based APIs
- When caching is critical
- Public APIs

Choose GraphQL for:
- Complex data requirements
- Mobile apps (reduce data transfer)
- Rapid frontend development
```

### Example 2: Using agents_ai for Architecture Design

```bash
$ agents_ai --collaborate "Design a microservices architecture for our e-commerce platform"

==================================================================
  Collaborative Task: Design a microservices architecture...
==================================================================

💭 AIC analyzing task...

AIC's Analysis:
------------------------------------------------------------------
From an operational perspective, I recommend:

1. Service Decomposition:
   - User Service (authentication, profiles)
   - Product Catalog Service
   - Order Management Service
   - Payment Service
   - Inventory Service
   - Notification Service

2. Technology Stack:
   - Containers: Docker + Kubernetes
   - API Gateway: Kong or AWS API Gateway
   - Message Queue: RabbitMQ or Kafka
   - Service Mesh: Istio for service-to-service communication

3. Data Management:
   - Database per service pattern
   - Event sourcing for order history
   - CQRS for product catalog

💭 Aria analyzing task...

Aria's Analysis:
------------------------------------------------------------------
From a philosophical and organizational perspective:

1. Service Boundaries:
   - Each service should have clear responsibility (Single Responsibility)
   - Bounded contexts aligned with business domains
   - Service autonomy promotes team independence

2. Communication Patterns:
   - Asynchronous messaging for loose coupling
   - Event-driven architecture for scalability
   - Clear API contracts as "social agreements"

3. Organizational Impact:
   - Conway's Law: Structure teams around services
   - Shared understanding through documentation
   - Cultural shift to distributed thinking

💭 Sora analyzing task...

Sora's Analysis:
------------------------------------------------------------------
From a formal and legal perspective:

1. Formal Requirements:
   - Strict API versioning and backward compatibility
   - Transaction boundaries and ACID compliance
   - Data consistency guarantees (eventual vs strong)

2. Legal Compliance:
   - GDPR: Data residency per service
   - PCI DSS: Payment service isolation
   - Audit logging across all services

3. Economic Modeling:
   - Cost attribution per service
   - Resource optimization based on usage
   - SLA definitions and penalties

==================================================================
  Synthesis
==================================================================

Combining all perspectives, here's the recommended architecture:
[Detailed synthesized architecture...]
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** - Always in `.gitignore`
2. **Use environment variables** - Don't hardcode API keys
3. **Rotate keys regularly** - Every 90 days minimum
4. **Set up billing alerts** - Monitor API usage costs
5. **Use read-only keys** - When possible, for agents
6. **Review agent proposals** - Before implementing code changes
7. **Limit agent file access** - Use workspace boundaries

---

## 📦 Installation Script

For a complete automated setup:

```bash
#!/bin/bash
# complete_setup.sh - Setup both AI systems

echo "Setting up AI Systems..."

# 1. Install Python dependencies
pip install openai anthropic google-genai cohere

# 2. Setup cursor_ai
bash setup_cursor_ai.sh

# 3. Setup agents_ai
bash setup_agents_ai.sh

# 4. Check API keys
echo ""
echo "Checking API keys..."
python cursor_ai.py --check-keys

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Add API keys to .env file (see .env.example)"
echo "2. Run: source ~/.zshrc (or ~/.bashrc)"
echo "3. Try: cursor_ai --get-keys"
echo "4. Try: agents_ai --help"
```

Save as `complete_setup.sh` and run:

```bash
bash complete_setup.sh
```

---

## 🤝 Contributing

To add new features:

### Adding a new AI provider to cursor_ai

1. Create provider class in `cursor_ai.py`
2. Add to `PROVIDERS` registry
3. Add to `PROVIDER_DISPLAY_NAMES`
4. Update `--get-keys` output
5. Update documentation

### Adding capabilities to agents_ai

1. Add to `AgentCapability` enum
2. Implement method in `AIAgent` class
3. Update agent initialization
4. Update `AGENTS_AI_GUIDE.md`

---

## 📚 Additional Resources

- **OpenAI Documentation**: https://platform.openai.com/docs
- **Anthropic Documentation**: https://docs.anthropic.com
- **Google AI Documentation**: https://ai.google.dev/docs
- **Multi-Agent Systems**: Research papers and articles
- **API Status Pages**: Check service health

---

## 📄 License

See project LICENSE file.

---

## 🆘 Support

For issues or questions:

1. Check documentation in this README
2. Review API_KEYS_GUIDE.md for API setup
3. Review AGENTS_AI_GUIDE.md for agent system details
4. Check API provider status pages
5. Review console output for error messages

---

## 🎉 Success!

You now have two powerful AI systems at your fingertips:

- **cursor_ai**: Chat with 10+ AI providers
- **agents_ai**: Multi-agent collaborative system with specialized agents

Both systems are production-ready and can significantly enhance your development workflow, code quality, and problem-solving capabilities.

Happy coding! 🚀
