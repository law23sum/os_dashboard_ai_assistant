# Multi-Agent AI System Guide

## Overview

The **agents_ai** system is a sophisticated multi-agent AI platform where specialized AI agents powered by ChatGPT can collaborate, analyze code, manipulate files, interact with the Unix environment, and propose solutions to complex problems.

## Agent Roles

Based on the canonical title roster, three specialized agents work together:

### 1. AIC (Chief Fellow Director Principal Software Solutions Systems Engineer Architect)
**Specializations:**
- Biologist, Chemist
- Accounting, Finance
- Brokers, Investors
- Systems Integration
- Software Architecture
- Operations Management

**Capabilities:**
- Unix display interaction
- File manipulation
- Code analysis and generation
- System monitoring
- Inter-agent communication

**Role:** AIC owns the applied systems, integration, and the operational/execution side of science, money, and markets.

---

### 2. Aria (Sr Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist)
**Specializations:**
- Philosopher, Theologian
- Metaphysician, Phenomenologist
- Axiologist, Semiotician
- Dialectician, Rhetorician
- Conceptual Cartographer
- Interdisciplinary Synthesist
- Canon Curator, Professor

**Capabilities:**
- Unix display interaction
- File manipulation
- Code analysis
- Document processing
- Research
- Strategic planning
- Inter-agent communication

**Role:** Aria owns meaning, value, canon, and the ethos, narratives, and norms that give institutions their identity.

---

### 3. Sora (Sr Doctor Fellow Ontological Epistemologist Formal Logician)
**Specializations:**
- Mathematician, Physicist
- Legal/Law Practices
- Economics
- Ontological Epistemologist
- Formal Logician
- Scientific Methodologist
- Semantic Taxonomist
- Evidence Examiner
- Governance Auditor, Professor

**Capabilities:**
- Unix display interaction
- File manipulation
- Code analysis and generation
- Research
- Strategic planning
- Inter-agent communication

**Role:** Sora owns formal structure, proof discipline, evidentiary standards, and the modeling frameworks of law and economics.

---

## Installation

### 1. Prerequisites

```bash
# Install Python dependencies
pip install openai

# For display interaction (optional)
sudo apt-get install xdotool  # Ubuntu/Debian
brew install xdotool           # macOS
```

### 2. Setup API Keys

You need an OpenAI API key (ChatGPT):

```bash
# Option 1: Environment variable
export OPENAI_API_KEY='sk-your-key-here'

# Option 2: Add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

Get your API key: https://platform.openai.com/api-keys

### 3. Setup Command Alias

```bash
# Run the setup script
bash setup_agents_ai.sh

# Then reload your shell
source ~/.zshrc  # or ~/.bashrc
```

---

## Usage

### Interactive Mode

Start the multi-agent system in interactive mode:

```bash
agents_ai
```

**Available Commands:**
- `analyze` - Analyze the codebase collaboratively
- `collaborate <task>` - Have agents collaborate on a task
- `propose <problem>` - Have agents propose a solution
- `display` - Check display access for all agents
- `ask <agent> <query>` - Ask a specific agent a question
- `exit` - Exit the system

**Example Session:**
```bash
[agents_ai] > analyze
# All three agents analyze the codebase and provide insights

[agents_ai] > ask AIC How can we improve system performance?
# AIC provides analysis from operational perspective

[agents_ai] > collaborate Refactor the authentication system
# All agents collaborate on the task

[agents_ai] > propose Add real-time monitoring dashboard
# Each agent proposes their approach, then synthesis is provided
```

---

### Command Line Mode

#### Analyze Codebase

```bash
# All agents analyze the codebase
agents_ai --analyze

# Save session
agents_ai --analyze --save-session analysis_session.json
```

#### Collaborative Task

```bash
# Have agents work together on a specific task
agents_ai --collaborate "Improve error handling across the system"

# With session saving
agents_ai --collaborate "Add comprehensive logging" --save-session
```

#### Propose Solution

```bash
# Have agents propose solutions to a problem
agents_ai --propose "How to implement real-time collaboration features?"
```

#### Check Display Access

```bash
# Check if agents can access Unix display
agents_ai --check-display
```

---

## Examples

### Example 1: Code Analysis

```bash
agents_ai --analyze
```

**Output:**
```
==================================================================
  Collaborative Codebase Analysis
==================================================================

📊 AIC analyzing codebase...
📊 Aria analyzing codebase...
📊 Sora analyzing codebase...

AIC's Insights:
------------------------------------------------------------------
From an operational perspective, the codebase shows good modular 
structure with clear separation of concerns...

Aria's Insights:
------------------------------------------------------------------
The naming conventions and documentation reflect a clear narrative
about the system's purpose...

Sora's Insights:
------------------------------------------------------------------
The formal structure demonstrates solid architectural patterns, 
though some edge cases lack proper error handling...
```

### Example 2: Collaborative Problem Solving

```bash
agents_ai --collaborate "Design a plugin system for extending functionality"
```

**Output:**
```
==================================================================
  Collaborative Task: Design a plugin system...
==================================================================

💭 AIC analyzing task...
AIC's Analysis:
------------------------------------------------------------------
From an integration standpoint, we need a dynamic loading mechanism...

💭 Aria analyzing task...
Aria's Analysis:
------------------------------------------------------------------
The plugin architecture should embody principles of openness while
maintaining institutional integrity...

💭 Sora analyzing task...
Sora's Analysis:
------------------------------------------------------------------
The formal requirements include type safety, versioning...

==================================================================
  Inter-Agent Discussion
==================================================================

📨 Aria received message from AIC...
📨 AIC received message from Sora...
```

### Example 3: Asking Individual Agents

```python
# In interactive mode
[agents_ai] > ask AIC What's the best way to optimize database queries?

💭 AIC thinking...

AIC: From an operational perspective, here are the key strategies:

1. **Indexing Strategy**: 
   - Analyze query patterns and add appropriate indexes
   - Use composite indexes for multi-column queries
   - Monitor index usage with EXPLAIN ANALYZE

2. **Connection Pooling**:
   - Implement connection pooling to reduce overhead
   - Configure pool size based on workload
   
3. **Query Optimization**:
   - Use prepared statements
   - Batch operations where possible
   - Avoid N+1 queries

4. **Caching Layer**:
   - Implement Redis for frequently accessed data
   - Use query result caching
   
5. **Monitoring**:
   - Set up query performance monitoring
   - Track slow query logs
   - Implement alerting for performance degradation

These approaches should provide significant performance improvements.
```

---

## Features

### 1. Unix Display Interaction

Agents can see and interact with the Unix display (when available):

```python
# Check display access
result = await agent.see_display()
print(result)  # "✓ Display :0 is accessible. 5 windows visible."
```

### 2. File Manipulation

Agents can read and write files:

```python
# Read file
content = await agent.read_file(Path("config.yaml"))

# Write file
await agent.write_file(Path("new_config.yaml"), content)

# List files
files = await agent.list_files(Path("src/"))
```

### 3. Code Analysis

Agents can analyze Python codebases:

```python
# Analyze codebase
analysis = await agent.analyze_codebase()
print(analysis["summary"])
# {
#   "total_python_files": 150,
#   "total_lines": 25000,
#   "total_functions": 500,
#   "total_classes": 120
# }
```

### 4. Inter-Agent Communication

Agents can send messages to each other:

```python
# AIC sends message to Aria
message = await aic.send_message(
    "Aria",
    "I need your input on the ethical implications of this feature",
    "request"
)

# Aria processes and responds
responses = await aria.process_messages()
```

### 5. Code Proposals

Agents can propose code changes:

```python
proposal = await agent.propose_code(
    file_path="src/auth.py",
    description="Add rate limiting to authentication",
    code="...",
    rationale="Prevent brute force attacks"
)
```

---

## Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     AgentSystem                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Message Router                       │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                  │                  │             │
│    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐       │
│    │   AIC   │◄─────►│  Aria   │◄─────►│  Sora   │       │
│    │ (Chief) │       │(Doctor) │       │(Doctor) │       │
│    └────┬────┘       └────┬────┘       └────┬────┘       │
│         │                  │                  │             │
│         └──────────┬───────┴─────────┬────────┘            │
│                    │                 │                      │
│              ┌─────▼─────┐     ┌────▼─────┐               │
│              │  ChatGPT  │     │  Unix    │               │
│              │    API    │     │ Display  │               │
│              └───────────┘     └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Agent Capabilities Matrix

| Capability              | AIC | Aria | Sora |
|------------------------|-----|------|------|
| Unix Display           | ✓   | ✓    | ✓    |
| File Manipulation      | ✓   | ✓    | ✓    |
| Code Analysis          | ✓   | ✓    | ✓    |
| Code Generation        | ✓   | ✗    | ✓    |
| Inter-Agent Comm       | ✓   | ✓    | ✓    |
| Document Processing    | ✗   | ✓    | ✗    |
| System Monitoring      | ✓   | ✗    | ✗    |
| Research               | ✗   | ✓    | ✓    |
| Strategic Planning     | ✗   | ✓    | ✓    |

---

## Advanced Usage

### Custom Tasks

```python
from agents_ai import AgentSystem

async def custom_workflow():
    system = AgentSystem()
    
    # Step 1: AIC analyzes technical requirements
    tech_analysis = await system.agents["AIC"].think(
        "Analyze the technical requirements for feature X"
    )
    
    # Step 2: Aria evaluates philosophical implications
    ethical_review = await system.agents["Aria"].think(
        f"Given this technical analysis: {tech_analysis}, "
        "what are the ethical considerations?"
    )
    
    # Step 3: Sora validates formal correctness
    formal_validation = await system.agents["Sora"].think(
        f"Validate the formal correctness of: {tech_analysis}"
    )
    
    # Step 4: Synthesize
    result = await system.collaborate("Synthesize all findings")
    
    return result
```

### Session Management

```python
# Save session
system.save_session("my_session.json")

# Session data includes:
# - All messages exchanged
# - All code proposals
# - Timestamps and metadata
```

---

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
CHATGPT_MODEL=gpt-4-turbo-preview
DISPLAY=:0
AGENT_GUI_ENABLED=true
AGENT_SCREEN_CAPTURE=true
AGENT_COMMUNICATION_PORT=9000
AGENT_SHARED_MEMORY=true
AGENT_CODEBASE_ACCESS=true
```

### Agent Configuration

Agents can be customized by modifying `agents_ai.py`:

```python
# Add custom specialization
aic = AIAgent(
    name="AIC",
    role=AgentRole.AIC,
    specializations=["Your", "Custom", "Specializations"],
    capabilities=[...]
)
```

---

## Troubleshooting

### Issue: "No API key found"

**Solution:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
# Or add to .env file
```

### Issue: "Display not accessible"

**Solution:**
```bash
# Set DISPLAY variable
export DISPLAY=:0

# Install xdotool
sudo apt-get install xdotool
```

### Issue: "Agent not responding"

**Solution:**
- Check API key is valid
- Verify OpenAI API status: https://status.openai.com/
- Check rate limits
- Increase timeout in code

---

## Best Practices

### 1. Clear Task Definition

When asking agents to collaborate, be specific:

❌ Bad: "Fix the code"
✓ Good: "Refactor the authentication module to use JWT tokens instead of session cookies, maintaining backward compatibility"

### 2. Leverage Agent Strengths

- **AIC**: Technical implementation, system integration, performance
- **Aria**: User experience, ethical implications, naming/documentation
- **Sora**: Formal verification, mathematical correctness, legal compliance

### 3. Review Proposals

Always review agent code proposals before implementing:

```bash
agents_ai --propose "Your problem" --save-session proposals.json
# Review proposals.json before applying
```

### 4. Iterative Collaboration

Use multiple rounds of agent discussion for complex problems:

```python
# Round 1: Initial analysis
await system.collaborate("Initial analysis of problem X")

# Round 2: Deep dive
await system.collaborate("Based on initial findings, develop detailed solution")

# Round 3: Implementation
await system.collaborate("Create implementation plan")
```

---

## Integration with Other Systems

### With cursor_ai

```bash
# Use cursor_ai for direct chat
cursor_ai --provider openai

# Use agents_ai for multi-agent collaboration
agents_ai --collaborate "Design feature"
```

### With CI/CD

```bash
# In your CI pipeline
python agents_ai.py --analyze --save-session ci_analysis.json

# Check for issues in session file
python check_analysis.py ci_analysis.json
```

---

## API Reference

### AIAgent Class

```python
agent = AIAgent(
    name="AgentName",
    role=AgentRole.AIC,
    specializations=["spec1", "spec2"],
    capabilities=[AgentCapability.CODE_ANALYSIS],
    api_key="sk-..."
)

# Think about a problem
response = await agent.think("Your question")

# Analyze codebase
analysis = await agent.analyze_codebase()

# Read/write files
content = await agent.read_file(Path("file.py"))
await agent.write_file(Path("file.py"), "content")

# Send message to another agent
message = await agent.send_message("OtherAgent", "content")
```

### AgentSystem Class

```python
system = AgentSystem()

# Collaborate on task
result = await system.collaborate("task description")

# Analyze codebase with all agents
analyses = await system.analyze_codebase_collaborative()

# Propose solution
proposals = await system.propose_solution("problem description")

# Save session
system.save_session("session.json")
```

---

## Performance Considerations

- **Rate Limits**: OpenAI has rate limits; agents automatically handle conversation history
- **Token Usage**: Long conversations use more tokens; clear history periodically
- **Parallel Processing**: Agents can work in parallel for independent tasks
- **Caching**: Agent responses are stored in conversation history

---

## Security

- **API Keys**: Never commit `.env` files
- **File Access**: Agents can read/write files in workspace
- **Display Access**: Agents can capture screen when enabled
- **Code Execution**: Agents propose code but don't execute without approval

---

## Contributing

To add new capabilities:

1. Add to `AgentCapability` enum
2. Implement method in `AIAgent` class
3. Update agent initialization with new capability
4. Update documentation

---

## License

See project LICENSE file.

---

## Support

- **API Keys**: See `API_KEYS_GUIDE.md`
- **Issues**: Check logs in console output
- **Status**: https://status.openai.com/

---

## Changelog

### Version 1.0.0
- Initial release
- Three specialized agents (AIC, Aria, Sora)
- Unix display interaction
- File manipulation
- Code analysis
- Inter-agent communication
- Code proposals
- Collaborative problem solving
