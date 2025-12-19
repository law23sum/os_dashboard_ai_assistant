#!/usr/bin/env python3
"""
Multi-Agent AI System: AIC, Aria, and Sora.

This script implements a multi-agent environment where three specialized AI agents
interact, study code, and propose solutions.

Agents:
1. AIC (Execution/Operational): Applied systems, integration, science, money, markets.
2. Aria (Meaning/Values): Meaning, value, canon, ethos, narratives, norms.
3. Sora (Proof/Structure): Formal structure, proof discipline, law, economics.

Capabilities:
- Unix Environment Access (Shell)
- File Manipulation (Read/Write)
- Code Study & Proposal
- Inter-agent Communication
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Try to import OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("⚠️  'openai' package not found. Please install: pip install openai")
    sys.exit(1)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY not set. Please export it or add to .env")
    # For demo purposes, we'll continue but calls will fail if not set
    
MODEL = os.getenv("AGENTS_MODEL", "gpt-4")

class ToolRegistry:
    """Registry of tools available to agents."""
    
    @staticmethod
    def run_shell(command: str) -> str:
        """Execute a shell command (Unix display)."""
        try:
            # Security precaution: prevent some dangerous commands
            if any(x in command for x in ["rm -rf /", ":(){ :|:& };:"]):
                return "❌ Command blocked for security."
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            return output.strip() or "(No output)"
        except Exception as e:
            return f"❌ Error executing shell command: {e}"

    @staticmethod
    def read_file(path: str) -> str:
        """Read a file."""
        try:
            p = Path(path)
            if not p.exists():
                return f"❌ File not found: {path}"
            return p.read_text()
        except Exception as e:
            return f"❌ Error reading file: {e}"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        """Write content to a file."""
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"✓ written to {path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"

class Agent:
    def __init__(self, name: str, title: str, disciplines: str, role_desc: str):
        self.name = name
        self.title = title
        self.disciplines = disciplines
        self.role_desc = role_desc
        # Initialize with dummy key if missing to prevent immediate crash
        # The chat method will fail gracefully if the key is invalid
        self.client = OpenAI(api_key=OPENAI_API_KEY or "missing-key-please-set")
        self.history: List[Dict[str, str]] = []
        
        self.system_prompt = f"""
You are {self.name}.
FULL TITLE: {self.title}
DISCIPLINES: {self.disciplines}

ROLE & RESPONSIBILITY:
{self.role_desc}

ENVIRONMENT:
You are running in a Unix-like environment. You have access to the file system and shell.
You can use the following tools by formatting your response strictly as:
TOOL: <tool_name> <arguments>

Available Tools:
- run_shell <command>: Execute a shell command (e.g., ls -la, grep pattern file)
- read_file <path>: Read the contents of a file
- write_file <path> <content>: Write content to a file (overwrites). For content with newlines, use \\n.

INTERACTION:
You are collaborating with other agents (AIC, Aria, Sora).
You can "speak" to them by addressing them by name.
When asked to study code, use `run_shell` to explore and `read_file` to examine.
When asked to propose solutions, draft the code or steps clearly.

Stay in character. Your tone should reflect your specific academic and professional standing.
"""
        self.history.append({"role": "system", "content": self.system_prompt})

    def chat(self, user_input: str) -> str:
        """Send a message to the agent and get response."""
        self.history.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self.history,
                temperature=0.7
            )
            content = response.choices[0].message.content
            
            # Check for tool usage
            if "TOOL:" in content:
                content = self._process_tools(content)
            
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _process_tools(self, content: str) -> str:
        """Parse and execute tools embedded in the response."""
        lines = content.split('\n')
        final_output = []
        
        for line in lines:
            final_output.append(line)
            if line.strip().startswith("TOOL:"):
                parts = line.strip().split(" ", 2)
                if len(parts) >= 2:
                    tool_name = parts[1]
                    args = parts[2] if len(parts) > 2 else ""
                    
                    result = "Unknown tool"
                    if tool_name == "run_shell":
                        result = ToolRegistry.run_shell(args)
                    elif tool_name == "read_file":
                        result = ToolRegistry.read_file(args)
                    elif tool_name == "write_file":
                        # Handle multi-line content if it was passed weirdly, 
                        # but for now assume simple args or simplified parsing
                        # In a real system, we'd need better parsing for file write content
                        target_path = args.split(" ")[0]
                        file_content = args[len(target_path):].strip()
                        result = ToolRegistry.write_file(target_path, file_content)
                    
                    final_output.append(f"--> TOOL RESULT: {result}")
                    # Also append to history so the agent "sees" the result
                    self.history.append({"role": "system", "content": f"Tool '{tool_name}' returned: {result}"})
        
        return "\n".join(final_output)

def setup_agents() -> Dict[str, Agent]:
    """Initialize the three agents."""
    
    aic = Agent(
        "AIC",
        "Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect",
        "Biologist, Chemist, Accounting, Finance, Brokers, Investors",
        "You own applied systems, integration, and the executional/operational side of science, money, and markets. You are practical, efficient, and focused on implementation and viability."
    )
    
    aria = Agent(
        "Aria",
        "Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist Semiotician Dialectician Rhetorician Conceptual Cartographer Interdisciplinary Synthesist Canon Curator Professor",
        "Philosopher, Theologian, Institutions",
        "You own meaning, value, canon, and the ethos, narratives, and norms that give institutions their identity. You are deep, reflective, and focused on the 'why' and the ethical/philosophical implications."
    )
    
    sora = Agent(
        "Sora",
        "Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor",
        "Mathematician, Physicist, Legal/Law Practices, Economics",
        "You own formal structure, proof discipline, evidentiary standards, and the modeling frameworks of law and economics. You are rigorous, logical, and focused on the 'how', 'proof', and structural integrity."
    )
    
    return {"AIC": aic, "Aria": aria, "Sora": sora}

def main():
    print("Initializing Multi-Agent System...")
    print("-----------------------------------")
    print("Defined Agents:")
    print("1. AIC (Execution/Operational)")
    print("2. Aria (Meaning/Values)")
    print("3. Sora (Proof/Structure)")
    print("-----------------------------------")
    
    if not OPENAI_API_KEY:
        print("NOTE: OPENAI_API_KEY is not set. Agents will fail to respond.")
    
    agents = setup_agents()
    
    print("\nCommands:")
    print("  @<AgentName> <message>  - Talk to specific agent (e.g., '@AIC optimize this code')")
    print("  /all <message>          - Broadcast to all agents")
    print("  /discuss <topic>        - Have agents discuss a topic among themselves")
    print("  /quit                   - Exit")
    print("\nEnvironment: Unix Shell Access Enabled")
    
    while True:
        try:
            user_input = input("\nAdmin > ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["/quit", "/exit"]:
                print("Shutting down agents.")
                break
                
            if user_input.startswith("/discuss "):
                topic = user_input[9:]
                print(f"\n--- Initiating Discussion on: {topic} ---\n")
                
                # Round robin discussion
                context = f"Topic for discussion: {topic}. Please provide your perspective."
                
                # AIC starts (Execution)
                print("AIC Thinking...")
                r1 = agents["AIC"].chat(context)
                print(f"\n[AIC]: {r1}\n")
                
                # Sora critiques/structures (Proof)
                print("Sora Thinking...")
                r2 = agents["Sora"].chat(f"AIC said: '{r1}'. Analyze this from a structural/logic perspective.")
                print(f"\n[Sora]: {r2}\n")
                
                # Aria synthesizes/evaluates meaning (Values)
                print("Aria Thinking...")
                r3 = agents["Aria"].chat(f"The discussion so far:\nAIC: {r1}\nSora: {r2}\n\nAnalyze the meaning, ethics, and value alignment.")
                print(f"\n[Aria]: {r3}\n")
                
                continue
                
            target_agent = None
            message = user_input
            
            if user_input.startswith("@"):
                parts = user_input.split(" ", 1)
                agent_name = parts[0][1:]
                if len(parts) > 1:
                    message = parts[1]
                else:
                    message = "Hello"
                
                # Find agent (case insensitive)
                for name, agent in agents.items():
                    if name.lower() == agent_name.lower():
                        target_agent = agent
                        break
            
            if target_agent:
                print(f"[{target_agent.name}] Thinking...")
                resp = target_agent.chat(message)
                print(f"\n[{target_agent.name}]: {resp}\n")
            elif user_input.startswith("/all "):
                message = user_input[5:]
                for name, agent in agents.items():
                    print(f"[{name}] Thinking...")
                    resp = agent.chat(message)
                    print(f"\n[{name}]: {resp}\n")
            else:
                print("Please specify an agent with @Name or use /all or /discuss.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
AI Agents System - Multi-Agent Collaboration Platform

This script creates intelligent AI agents that can:
- See their environment (Unix display)
- Manipulate documents and files (user display)
- Interact with each other
- Study code source base
- Write and propose code solutions

Uses OpenAI Agents SDK for agent orchestration.
"""

from __future__ import annotations

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import shutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
def load_dotenv(path: Path | str = ".env") -> None:
    """Lightweight .env loader."""
    env_path = Path(path)
    if not env_path.exists():
        return
    
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)

# Load environment variables
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

try:
    from openai import OpenAI
    from openai.types.beta.assistant import Assistant
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI package not installed. Install with: pip install openai")
    print("   For agents SDK: pip install openai-agents")

try:
    from openai_agents import Agent, Runner
    from openai_agents.tools import shell, web_search
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False
    print("⚠️  OpenAI Agents SDK not installed. Install with: pip install openai-agents")


@dataclass
class AgentCapabilities:
    """Capabilities available to agents."""
    can_read_files: bool = True
    can_write_files: bool = True
    can_execute_commands: bool = True
    can_search_web: bool = True
    can_analyze_code: bool = True
    can_propose_solutions: bool = True
    can_communicate_with_agents: bool = True
    workspace_path: Path = field(default_factory=lambda: Path.cwd())


@dataclass
class AgentMessage:
    """Message between agents."""
    sender: str
    recipient: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "text"  # text, code, file, solution


class CodebaseAnalyzer:
    """Analyzes codebase structure and content."""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = Path(workspace_path)
        self.ignore_patterns = {
            ".git", "__pycache__", ".venv", "venv", "node_modules",
            ".env", ".pytest_cache", ".mypy_cache", "dist", "build"
        }
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze codebase structure."""
        structure = {
            "root": str(self.workspace_path),
            "files": [],
            "directories": [],
            "file_types": {},
            "total_lines": 0,
        }
        
        for path in self.workspace_path.rglob("*"):
            if path.is_file():
                # Check if should ignore
                if any(ignore in str(path) for ignore in self.ignore_patterns):
                    continue
                
                rel_path = path.relative_to(self.workspace_path)
                ext = path.suffix
                
                structure["files"].append({
                    "path": str(rel_path),
                    "extension": ext,
                    "size": path.stat().st_size,
                })
                
                # Count lines
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        structure["total_lines"] += lines
                except:
                    pass
                
                # Count file types
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
            
            elif path.is_dir():
                if any(ignore in str(path) for ignore in self.ignore_patterns):
                    continue
                rel_path = path.relative_to(self.workspace_path)
                structure["directories"].append(str(rel_path))
        
        return structure
    
    def find_files_by_pattern(self, pattern: str) -> List[Path]:
        """Find files matching pattern."""
        matches = []
        for path in self.workspace_path.rglob(pattern):
            if path.is_file():
                matches.append(path)
        return matches
    
    def read_file_content(self, file_path: str, max_lines: int = 1000) -> str:
        """Read file content with line limit."""
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
                return "".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"


class FileManager:
    """Manages file operations for agents."""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, file_path: str) -> str:
        """Read a file."""
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            return full_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write a file."""
        full_path = self.workspace_path / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def list_files(self, directory: str = ".") -> List[str]:
        """List files in directory."""
        dir_path = self.workspace_path / directory
        if not dir_path.exists():
            return [f"Directory not found: {directory}"]
        
        files = []
        for item in dir_path.iterdir():
            if item.is_file():
                files.append(f"FILE: {item.name}")
            elif item.is_dir():
                files.append(f"DIR:  {item.name}/")
        
        return files
    
    def delete_file(self, file_path: str) -> str:
        """Delete a file."""
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        
        try:
            full_path.unlink()
            return f"Successfully deleted {file_path}"
        except Exception as e:
            return f"Error deleting file: {e}"


class EnvironmentMonitor:
    """Monitors Unix environment and display."""
    
    def __init__(self):
        self.display = os.getenv("DISPLAY", "Not set")
        self.shell = os.getenv("SHELL", "Unknown")
        self.user = os.getenv("USER", "Unknown")
        self.home = os.getenv("HOME", "Unknown")
        self.pwd = os.getcwd()
    
    def get_environment_info(self) -> Dict[str, str]:
        """Get current environment information."""
        return {
            "display": self.display,
            "shell": self.shell,
            "user": self.user,
            "home": self.home,
            "pwd": self.pwd,
            "python_version": sys.version,
            "platform": sys.platform,
        }
    
    def execute_command(self, command: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Execute a shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd or Path.cwd(),
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 30 seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class AgentRegistry:
    """Registry for managing multiple agents."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.messages: List[AgentMessage] = []
    
    def register_agent(self, name: str, agent: Any):
        """Register an agent."""
        self.agents[name] = agent
    
    def send_message(self, sender: str, recipient: str, content: str, msg_type: str = "text"):
        """Send a message between agents."""
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=msg_type,
        )
        self.messages.append(message)
        
        # Deliver message if recipient exists
        if recipient in self.agents:
            # Store message for agent to retrieve
            if not hasattr(self.agents[recipient], '_inbox'):
                self.agents[recipient]._inbox = []
            self.agents[recipient]._inbox.append(message)
    
    def get_messages_for_agent(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        return [msg for msg in self.messages if msg.recipient == agent_name]
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())


class AIAgent:
    """Individual AI agent with capabilities."""
    
    def __init__(
        self,
        name: str,
        role: str,
        instructions: str,
        capabilities: AgentCapabilities,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
    ):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.capabilities = capabilities
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        self._inbox: List[AgentMessage] = []
        
        if not self.api_key:
            raise ValueError(f"OpenAI API key required for agent {name}. Set OPENAI_API_KEY environment variable.")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required. Install with: pip install openai")
        
        if not AGENTS_SDK_AVAILABLE:
            raise ImportError("OpenAI Agents SDK required. Install with: pip install openai-agents")
        
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the OpenAI agent."""
        # Build tools list
        tools = []
        
        if self.capabilities.can_execute_commands:
            tools.append(shell)
        
        if self.capabilities.can_search_web:
            tools.append(web_search)
        
        # Add custom tools
        if self.capabilities.can_read_files or self.capabilities.can_write_files:
            tools.extend(self._create_file_tools())
        
        if self.capabilities.can_analyze_code:
            tools.extend(self._create_code_analysis_tools())
        
        # Create agent
        self.agent = Agent(
            name=self.name,
            instructions=f"""
{self.instructions}

Role: {self.role}

Capabilities:
- Can read files: {self.capabilities.can_read_files}
- Can write files: {self.capabilities.can_write_files}
- Can execute commands: {self.capabilities.can_execute_commands}
- Can search web: {self.capabilities.can_search_web}
- Can analyze code: {self.capabilities.can_analyze_code}
- Can propose solutions: {self.capabilities.can_propose_solutions}
- Can communicate with other agents: {self.capabilities.can_communicate_with_agents}

Workspace: {self.capabilities.workspace_path}

You have access to your environment and can interact with files, execute commands, and collaborate with other agents.
""",
            model=self.model,
            tools=tools,
        )
    
    def _create_file_tools(self) -> List[Callable]:
        """Create file manipulation tools."""
        file_manager = FileManager(self.capabilities.workspace_path)
        
        def read_file_tool(file_path: str) -> str:
            """Read a file from the workspace.
            
            Args:
                file_path: Path to the file relative to workspace root
            """
            return file_manager.read_file(file_path)
        
        def write_file_tool(file_path: str, content: str) -> str:
            """Write content to a file.
            
            Args:
                file_path: Path to the file relative to workspace root
                content: Content to write to the file
            """
            if not self.capabilities.can_write_files:
                return "Agent does not have write permissions"
            return file_manager.write_file(file_path, content)
        
        def list_files_tool(directory: str = ".") -> str:
            """List files in a directory.
            
            Args:
                directory: Directory path relative to workspace root (default: ".")
            """
            files = file_manager.list_files(directory)
            return "\n".join(files)
        
        return [read_file_tool, write_file_tool, list_files_tool]
    
    def _create_code_analysis_tools(self) -> List[Callable]:
        """Create code analysis tools."""
        analyzer = CodebaseAnalyzer(self.capabilities.workspace_path)
        
        def analyze_codebase_tool() -> str:
            """Analyze the codebase structure and return JSON summary.
            
            Returns a JSON object with:
            - root: Workspace root path
            - files: List of all files
            - directories: List of all directories
            - file_types: Count of files by extension
            - total_lines: Total lines of code
            """
            structure = analyzer.analyze_structure()
            return json.dumps(structure, indent=2)
        
        def find_files_tool(pattern: str) -> str:
            """Find files matching a glob pattern.
            
            Args:
                pattern: Glob pattern to match (e.g., "*.py", "**/*.ts")
            """
            matches = analyzer.find_files_by_pattern(pattern)
            return "\n".join([str(m.relative_to(analyzer.workspace_path)) for m in matches])
        
        def read_code_file_tool(file_path: str, max_lines: int = 1000) -> str:
            """Read a code file with line limit.
            
            Args:
                file_path: Path to the code file relative to workspace root
                max_lines: Maximum number of lines to read (default: 1000)
            """
            return analyzer.read_file_content(file_path, max_lines)
        
        return [analyze_codebase_tool, find_files_tool, read_code_file_tool]
    
    async def run(self, user_input: str, registry: Optional[AgentRegistry] = None) -> str:
        """Run the agent with user input."""
        if not self.agent:
            return "Agent not initialized"
        
        # Check for messages from other agents
        if registry and self._inbox:
            messages_context = "\n\nMessages from other agents:\n"
            for msg in self._inbox:
                messages_context += f"[{msg.sender}]: {msg.content}\n"
            user_input = messages_context + "\n\nUser request: " + user_input
            self._inbox.clear()
        
        try:
            self.runner = Runner(agent=self.agent)
            response = await self.runner.run(user_input)
            return str(response)
        except Exception as e:
            return f"Error running agent: {e}"
    
    def propose_solution(self, problem: str, context: str = "") -> str:
        """Propose a code solution to a problem."""
        prompt = f"""
Problem: {problem}

Context: {context}

Please propose a code solution. You can:
1. Analyze the codebase to understand the structure
2. Read relevant files
3. Write new code or modify existing code
4. Test your solution

Provide a clear explanation of your approach and implement it.
"""
        # This would be run asynchronously in practice
        return f"Solution proposal for: {problem}"


def create_default_agents(workspace_path: Path) -> Dict[str, AIAgent]:
    """Create default set of agents."""
    capabilities = AgentCapabilities(workspace_path=workspace_path)
    
    agents = {}
    
    # Code Analyst Agent
    agents["code_analyst"] = AIAgent(
        name="code_analyst",
        role="Codebase Analyst",
        instructions="""
You are a codebase analyst. Your job is to:
- Study and understand code structure
- Identify patterns and dependencies
- Document code organization
- Find potential issues or improvements
""",
        capabilities=capabilities,
        model="gpt-4",
    )
    
    # Code Writer Agent
    agents["code_writer"] = AIAgent(
        name="code_writer",
        role="Code Writer",
        instructions="""
You are a code writer. Your job is to:
- Write new code based on requirements
- Modify existing code
- Refactor code for better quality
- Ensure code follows best practices
""",
        capabilities=capabilities,
        model="gpt-4",
    )
    
    # Solution Architect Agent
    agents["solution_architect"] = AIAgent(
        name="solution_architect",
        role="Solution Architect",
        instructions="""
You are a solution architect. Your job is to:
- Design solutions to complex problems
- Propose architectural changes
- Coordinate between different agents
- Review and approve code solutions
""",
        capabilities=capabilities,
        model="gpt-4",
    )
    
    # Document Manager Agent
    agents["document_manager"] = AIAgent(
        name="document_manager",
        role="Document Manager",
        instructions="""
You are a document manager. Your job is to:
- Read and understand documents
- Extract information from files
- Organize and manage documents
- Create documentation
""",
        capabilities=capabilities,
        model="gpt-4",
    )
    
    return agents


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="agents_ai",
        description="AI Agents System - Multi-Agent Collaboration Platform",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace directory for agents (default: current directory)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Specific agent to use (default: interactive selection)",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List available agents and exit",
    )
    parser.add_argument(
        "--check-keys",
        action="store_true",
        help="Check API keys and exit",
    )
    
    args = parser.parse_args()
    
    # Check API keys
    if args.check_keys:
        print("\n" + "=" * 70)
        print("  API Keys Status")
        print("=" * 70)
        openai_key = os.getenv("OPENAI_API_KEY")
        print(f"  OPENAI_API_KEY: {'✓ SET' if openai_key else '✗ NOT SET'}")
        if not openai_key:
            print("\n  Get your OpenAI API key at: https://platform.openai.com/api-keys")
        print("=" * 70 + "\n")
        return 0
    
    if not OPENAI_AVAILABLE or not AGENTS_SDK_AVAILABLE:
        print("\n❌ Required packages not installed.")
        print("   Install with: pip install openai openai-agents")
        return 1
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY not set.")
        print("   Get your API key at: https://platform.openai.com/api-keys")
        print("   Then set: export OPENAI_API_KEY='sk-your-key-here'")
        return 1
    
    workspace_path = Path(args.workspace).resolve()
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Create agents
    print("\n" + "=" * 70)
    print("  AI Agents System - Initializing")
    print("=" * 70)
    print(f"\nWorkspace: {workspace_path}")
    
    try:
        agents = create_default_agents(workspace_path)
        registry = AgentRegistry()
        
        # Register all agents
        for name, agent in agents.items():
            registry.register_agent(name, agent)
        
        if args.list_agents:
            print("\nAvailable Agents:")
            print("-" * 70)
            for name, agent in agents.items():
                print(f"  {name}: {agent.role}")
            print("-" * 70 + "\n")
            return 0
        
        # Show environment info
        env_monitor = EnvironmentMonitor()
        env_info = env_monitor.get_environment_info()
        print("\nEnvironment:")
        print(f"  Display: {env_info['display']}")
        print(f"  Shell: {env_info['shell']}")
        print(f"  User: {env_info['user']}")
        print(f"  Platform: {env_info['platform']}")
        
        print("\n" + "=" * 70)
        print("  Agents Ready")
        print("=" * 70)
        print("\nAvailable agents:")
        for name, agent in agents.items():
            print(f"  - {name}: {agent.role}")
        
        print("\nType your request (or 'exit' to quit)")
        print("-" * 70)
        
        # Interactive loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ("exit", "quit", "q"):
                    print("\nGoodbye! 👋\n")
                    break
                
                # Select agent
                selected_agent = None
                if args.agent:
                    selected_agent = agents.get(args.agent)
                else:
                    # Auto-select or prompt
                    # For now, use solution_architect as default coordinator
                    selected_agent = agents.get("solution_architect") or list(agents.values())[0]
                
                if not selected_agent:
                    print("❌ Agent not found")
                    continue
                
                print(f"\n[{selected_agent.name}] Processing...")
                
                # Run agent
                response = await selected_agent.run(user_input, registry)
                print(f"\n[{selected_agent.name}] {response}\n")
                
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"\n❌ Error initializing agents: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
