#!/usr/bin/env python3
"""
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
