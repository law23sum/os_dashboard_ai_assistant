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
