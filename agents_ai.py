#!/usr/bin/env python3
"""
Multi-Agent AI System - agents_ai

A sophisticated multi-agent system with specialized AI agents that can:
- See and interact with the Unix environment (display)
- Manipulate documents and files
- Communicate and collaborate with each other
- Analyze and study code repositories
- Write and propose code solutions

Agents:
- AIC (Sir Chief Fellow Director): Biologist, Chemist, Accounting, Finance, Brokers, Investors
  Owns applied systems, integration, and the executionaloperational side of science, money, and markets
  
- Aria (Sr Doctor Fellow): Philosopher, Theologian, Institutions
  Owns meaning, value, canon, and the ethos, narratives, and norms that give institutions their identity
  
- Sora (Sr Doctor Fellow): Mathematician, Physicist, Legal/Law Practices, Economics
  Owns formal structure, proof discipline, evidentiary standards, and the modeling frameworks of law and economics

Each agent uses ChatGPT's API (OpenAI) for their intelligence and can see the Unix display, 
manipulate files, and collaborate on complex tasks.

Usage:
    python agents_ai.py                     # Interactive multi-agent session
    python agents_ai.py --task "analyze codebase"  # Run specific task
    python agents_ai.py --collaborate       # Agent collaboration mode
"""

from __future__ import annotations

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import ast
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
def load_dotenv(path: Path | str = ".env") -> None:
    """Lightweight .env loader to avoid external dependency."""
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

env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)


class AgentRole(Enum):
    """Agent role types based on canonical title roster"""
    AIC = "AIC"  # Chief - Applied systems, execution, operational
    ARIA = "ARIA"  # Doctor - Meaning, value, institutions
    SORA = "SORA"  # Doctor - Formal structure, proof, law/economics


class AgentCapability(Enum):
    """Capabilities each agent can have"""
    UNIX_DISPLAY = "unix_display"
    FILE_MANIPULATION = "file_manipulation"
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    INTER_AGENT_COMM = "inter_agent_communication"
    DOCUMENT_PROCESSING = "document_processing"
    SYSTEM_MONITORING = "system_monitoring"
    RESEARCH = "research"
    STRATEGIC_PLANNING = "strategic_planning"


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    sender: str
    recipient: str
    content: str
    timestamp: datetime
    message_type: str = "general"  # general, request, response, proposal
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "metadata": self.metadata
        }


@dataclass
class CodeProposal:
    """Structure for code proposals from agents"""
    agent: str
    file_path: str
    description: str
    code: str
    rationale: str
    timestamp: datetime
    approved: bool = False
    reviewed_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "file_path": self.file_path,
            "description": self.description,
            "code": self.code,
            "rationale": self.rationale,
            "timestamp": self.timestamp.isoformat(),
            "approved": self.approved,
            "reviewed_by": self.reviewed_by
        }


class AIAgent:
    """Base class for AI agents with ChatGPT integration"""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        specializations: List[str],
        capabilities: List[AgentCapability],
        api_key: Optional[str] = None
    ):
        self.name = name
        self.role = role
        self.specializations = specializations
        self.capabilities = capabilities
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("CHATGPT_API_KEY")
        self.client = None
        self.conversation_history: List[Dict[str, str]] = []
        self.message_queue: List[AgentMessage] = []
        self.code_proposals: List[CodeProposal] = []
        self.workspace_path = project_root
        self.display = os.getenv("DISPLAY", ":0")
        
        # Initialize OpenAI client
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize OpenAI/ChatGPT client"""
        if not self.api_key:
            print(f"⚠️  {self.name}: No API key found. Set OPENAI_API_KEY or CHATGPT_API_KEY")
            return False
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            return True
        except ImportError:
            print(f"⚠️  {self.name}: openai package not installed. Install with: pip install openai")
            return False
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        base_prompt = f"""You are {self.name}, a specialized AI agent with the role of {self.role.value}.

Your specializations: {', '.join(self.specializations)}

Your capabilities include:
{chr(10).join(f'- {cap.value}' for cap in self.capabilities)}

You are part of a multi-agent system where:
- AIC (Chief) handles applied systems, integration, execution, and operational aspects
- Aria (Doctor) handles meaning, value, canon, and institutional identity
- Sora (Doctor) handles formal structure, proof, evidentiary standards, and modeling

Your role in this system: {self._get_role_description()}

When analyzing code, provide detailed insights about architecture, patterns, and improvements.
When proposing code, explain your rationale and consider the broader system impact.
When collaborating with other agents, be clear and constructive.
"""
        return base_prompt
    
    def _get_role_description(self) -> str:
        """Get detailed role description"""
        if self.role == AgentRole.AIC:
            return """You own the applied side of systems, focusing on:
- Integration and practical implementation
- Operational efficiency and execution
- Scientific and financial applications
- Market dynamics and investment strategies
- System reliability and performance"""
        elif self.role == AgentRole.ARIA:
            return """You own the meaning and value layer, focusing on:
- Philosophical and theological frameworks
- Institutional identity and ethos
- Narratives and norms that guide behavior
- Ethical considerations and values
- Cultural and organizational canon"""
        elif self.role == AgentRole.SORA:
            return """You own the formal structure layer, focusing on:
- Mathematical rigor and proofs
- Physical laws and constraints
- Legal frameworks and compliance
- Economic modeling and analysis
- Evidentiary standards and validation"""
        return ""
    
    async def think(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Think about a problem using ChatGPT"""
        if not self.client:
            return "❌ Agent not initialized. Please set OPENAI_API_KEY."
        
        # Build context-aware prompt
        full_prompt = prompt
        if context:
            context_str = json.dumps(context, indent=2)
            full_prompt = f"{prompt}\n\nContext:\n{context_str}"
        
        # Add to conversation history
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
        ]
        
        # Add relevant conversation history (last 10 messages)
        messages.extend(self.conversation_history[-10:])
        
        # Add current prompt
        messages.append({"role": "user", "content": full_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("CHATGPT_MODEL", "gpt-4-turbo-preview"),
                messages=messages,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # Limit history size
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return answer
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def see_display(self) -> str:
        """See the Unix display (capture screen)"""
        if AgentCapability.UNIX_DISPLAY not in self.capabilities:
            return "❌ This agent doesn't have display viewing capability"
        
        try:
            # Check if DISPLAY is set
            if not self.display:
                return "❌ No DISPLAY environment variable set"
            
            # List X windows
            result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", "."],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                windows = result.stdout.strip().split('\n')
                return f"✓ Display {self.display} is accessible. {len(windows)} windows visible."
            else:
                return f"⚠️  Display accessible but no windows found"
        
        except FileNotFoundError:
            return "⚠️  xdotool not installed. Install with: sudo apt-get install xdotool"
        except Exception as e:
            return f"⚠️  Error accessing display: {str(e)}"
    
    async def list_files(self, directory: Optional[Path] = None) -> List[Path]:
        """List files in a directory"""
        if AgentCapability.FILE_MANIPULATION not in self.capabilities:
            return []
        
        target_dir = directory or self.workspace_path
        try:
            files = list(target_dir.rglob("*"))
            return [f for f in files if f.is_file()]
        except Exception as e:
            print(f"❌ {self.name}: Error listing files: {e}")
            return []
    
    async def read_file(self, file_path: Path) -> Optional[str]:
        """Read a file"""
        if AgentCapability.FILE_MANIPULATION not in self.capabilities:
            return None
        
        try:
            return file_path.read_text()
        except Exception as e:
            print(f"❌ {self.name}: Error reading file {file_path}: {e}")
            return None
    
    async def write_file(self, file_path: Path, content: str) -> bool:
        """Write content to a file"""
        if AgentCapability.FILE_MANIPULATION not in self.capabilities:
            return False
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return True
        except Exception as e:
            print(f"❌ {self.name}: Error writing file {file_path}: {e}")
            return False
    
    async def analyze_codebase(self, directory: Optional[Path] = None) -> Dict[str, Any]:
        """Analyze the codebase"""
        if AgentCapability.CODE_ANALYSIS not in self.capabilities:
            return {"error": "Code analysis not available for this agent"}
        
        target_dir = directory or self.workspace_path
        
        analysis = {
            "agent": self.name,
            "directory": str(target_dir),
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "summary": {}
        }
        
        # Find Python files
        py_files = list(target_dir.glob("**/*.py"))
        
        total_lines = 0
        total_functions = 0
        total_classes = 0
        
        for py_file in py_files[:50]:  # Limit to first 50 files
            try:
                content = py_file.read_text()
                lines = len(content.split('\n'))
                total_lines += lines
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    total_functions += len(functions)
                    total_classes += len(classes)
                    
                    analysis["files"][str(py_file)] = {
                        "lines": lines,
                        "functions": functions,
                        "classes": classes
                    }
                except SyntaxError:
                    pass
            
            except Exception as e:
                continue
        
        analysis["summary"] = {
            "total_python_files": len(py_files),
            "analyzed_files": len(analysis["files"]),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes
        }
        
        return analysis
    
    async def propose_code(
        self,
        file_path: str,
        description: str,
        code: str,
        rationale: str
    ) -> CodeProposal:
        """Propose a code change or new file"""
        proposal = CodeProposal(
            agent=self.name,
            file_path=file_path,
            description=description,
            code=code,
            rationale=rationale,
            timestamp=datetime.now()
        )
        
        self.code_proposals.append(proposal)
        return proposal
    
    async def send_message(self, recipient: str, content: str, message_type: str = "general") -> AgentMessage:
        """Send a message to another agent"""
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type
        )
        return message
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent"""
        self.message_queue.append(message)
        print(f"\n📨 {self.name} received message from {message.sender}:")
        print(f"   {message.content[:100]}...")
    
    async def process_messages(self) -> List[AgentMessage]:
        """Process pending messages and generate responses"""
        responses = []
        
        for message in self.message_queue:
            # Think about the message
            response_content = await self.think(
                f"You received a message from {message.sender}: {message.content}\n\nProvide a thoughtful response.",
                context={"message_type": message.message_type, "sender_role": message.sender}
            )
            
            # Create response
            response = await self.send_message(
                recipient=message.sender,
                content=response_content,
                message_type="response"
            )
            responses.append(response)
        
        # Clear processed messages
        self.message_queue.clear()
        
        return responses


class AgentSystem:
    """Multi-agent system coordinator"""
    
    def __init__(self):
        self.agents: Dict[str, AIAgent] = {}
        self.message_log: List[AgentMessage] = []
        self.proposal_log: List[CodeProposal] = []
        self.workspace_path = project_root
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Initialize the three main agents"""
        
        # AIC - Chief Fellow Director Principal Software Solutions Systems Engineer Architect
        aic = AIAgent(
            name="AIC",
            role=AgentRole.AIC,
            specializations=[
                "Biologist", "Chemist", "Accounting", "Finance", 
                "Brokers", "Investors", "Systems Integration",
                "Software Architecture", "Operations"
            ],
            capabilities=[
                AgentCapability.UNIX_DISPLAY,
                AgentCapability.FILE_MANIPULATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_GENERATION,
                AgentCapability.INTER_AGENT_COMM,
                AgentCapability.SYSTEM_MONITORING,
            ]
        )
        
        # Aria - Sr Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist
        aria = AIAgent(
            name="Aria",
            role=AgentRole.ARIA,
            specializations=[
                "Philosopher", "Theologian", "Metaphysician",
                "Phenomenologist", "Axiologist", "Semiotician",
                "Dialectician", "Rhetorician", "Conceptual Cartographer",
                "Interdisciplinary Synthesist", "Canon Curator", "Professor"
            ],
            capabilities=[
                AgentCapability.UNIX_DISPLAY,
                AgentCapability.FILE_MANIPULATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.INTER_AGENT_COMM,
                AgentCapability.DOCUMENT_PROCESSING,
                AgentCapability.RESEARCH,
                AgentCapability.STRATEGIC_PLANNING,
            ]
        )
        
        # Sora - Sr Doctor Fellow Ontological Epistemologist Formal Logician
        sora = AIAgent(
            name="Sora",
            role=AgentRole.SORA,
            specializations=[
                "Mathematician", "Physicist", "Legal Practices",
                "Economics", "Ontological Epistemologist",
                "Formal Logician", "Scientific Methodologist",
                "Semantic Taxonomist", "Evidence Examiner",
                "Governance Auditor", "Professor"
            ],
            capabilities=[
                AgentCapability.UNIX_DISPLAY,
                AgentCapability.FILE_MANIPULATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_GENERATION,
                AgentCapability.INTER_AGENT_COMM,
                AgentCapability.RESEARCH,
                AgentCapability.STRATEGIC_PLANNING,
            ]
        )
        
        self.agents = {
            "AIC": aic,
            "Aria": aria,
            "Sora": sora
        }
        
        print("\n" + "=" * 70)
        print("  Multi-Agent AI System Initialized")
        print("=" * 70)
        print(f"\n✓ AIC initialized - {len(aic.specializations)} specializations")
        print(f"✓ Aria initialized - {len(aria.specializations)} specializations")
        print(f"✓ Sora initialized - {len(sora.specializations)} specializations")
        print()
    
    async def route_message(self, message: AgentMessage) -> None:
        """Route a message to the appropriate agent"""
        if message.recipient in self.agents:
            await self.agents[message.recipient].receive_message(message)
            self.message_log.append(message)
    
    async def collaborate(self, task: str) -> Dict[str, Any]:
        """Have all agents collaborate on a task"""
        print(f"\n{'='*70}")
        print(f"  Collaborative Task: {task}")
        print(f"{'='*70}\n")
        
        results = {}
        
        # Each agent thinks about the task from their perspective
        for agent_name, agent in self.agents.items():
            print(f"\n💭 {agent_name} analyzing task...")
            
            prompt = f"""Analyze this task from your specialized perspective:

Task: {task}

Consider:
1. Your role: {agent.role.value}
2. Your specializations: {', '.join(agent.specializations)}
3. How you can contribute to solving this task
4. What other agents (AIC, Aria, Sora) might need to handle
5. Specific actions you recommend

Provide a detailed analysis and recommendations."""
            
            response = await agent.think(prompt)
            results[agent_name] = response
            
            print(f"\n{agent_name}'s Analysis:")
            print("-" * 70)
            print(response[:500] + "..." if len(response) > 500 else response)
        
        # Agents discuss with each other
        print(f"\n{'='*70}")
        print("  Inter-Agent Discussion")
        print(f"{'='*70}\n")
        
        # AIC initiates discussion
        aic_message = await self.agents["AIC"].send_message(
            "Aria",
            f"Based on my analysis of '{task}', I need your input on the philosophical and institutional implications. How should we frame this solution?",
            "request"
        )
        await self.route_message(aic_message)
        
        # Aria responds
        aria_responses = await self.agents["Aria"].process_messages()
        for response in aria_responses:
            await self.route_message(response)
        
        # Sora chimes in
        sora_message = await self.agents["Sora"].send_message(
            "AIC",
            f"I've reviewed the formal requirements for '{task}'. Let me provide the mathematical and legal framework we should follow.",
            "request"
        )
        await self.route_message(sora_message)
        
        return {
            "task": task,
            "individual_analyses": results,
            "messages_exchanged": len(self.message_log),
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze_codebase_collaborative(self) -> Dict[str, Any]:
        """Have all agents analyze the codebase together"""
        print(f"\n{'='*70}")
        print("  Collaborative Codebase Analysis")
        print(f"{'='*70}\n")
        
        analyses = {}
        
        for agent_name, agent in self.agents.items():
            if AgentCapability.CODE_ANALYSIS in agent.capabilities:
                print(f"📊 {agent_name} analyzing codebase...")
                analysis = await agent.analyze_codebase()
                analyses[agent_name] = analysis
                
                # Agent provides commentary
                summary = analysis.get("summary", {})
                prompt = f"""You've analyzed the codebase and found:
- {summary.get('total_python_files', 0)} Python files
- {summary.get('total_lines', 0)} lines of code
- {summary.get('total_functions', 0)} functions
- {summary.get('total_classes', 0)} classes

From your perspective as {agent.role.value}, provide insights about:
1. Code quality and architecture
2. Potential improvements
3. Areas of concern
4. Recommendations

Be specific and actionable."""
                
                insights = await agent.think(prompt, context=analysis)
                analyses[f"{agent_name}_insights"] = insights
                
                print(f"\n{agent_name}'s Insights:")
                print("-" * 70)
                print(insights[:400] + "..." if len(insights) > 400 else insights)
        
        return analyses
    
    async def propose_solution(self, problem: str) -> Dict[str, Any]:
        """Have agents propose a solution to a problem"""
        print(f"\n{'='*70}")
        print(f"  Solution Proposal for: {problem}")
        print(f"{'='*70}\n")
        
        proposals = {}
        
        for agent_name, agent in self.agents.items():
            print(f"\n💡 {agent_name} proposing solution...")
            
            prompt = f"""Problem: {problem}

As {agent.role.value} with expertise in {', '.join(agent.specializations[:3])}, 
propose a detailed solution. Include:

1. Analysis of the problem
2. Proposed solution approach
3. Implementation steps
4. Potential challenges
5. Success criteria

If this requires code changes, describe what files/functions need to be modified."""
            
            proposal = await agent.think(prompt)
            proposals[agent_name] = proposal
            
            print(f"\n{agent_name}'s Proposal:")
            print("-" * 70)
            print(proposal[:500] + "..." if len(proposal) > 500 else proposal)
        
        # Synthesize proposals
        print(f"\n{'='*70}")
        print("  Synthesizing Proposals")
        print(f"{'='*70}\n")
        
        synthesis_prompt = f"""Review these three proposals for: {problem}

AIC's Proposal (Applied/Operational):
{proposals['AIC'][:500]}

Aria's Proposal (Meaning/Value):
{proposals['Aria'][:500]}

Sora's Proposal (Formal/Structural):
{proposals['Sora'][:500]}

Provide a synthesized solution that integrates all three perspectives."""
        
        synthesis = await self.agents["AIC"].think(synthesis_prompt)
        
        print("Synthesized Solution:")
        print("-" * 70)
        print(synthesis)
        
        return {
            "problem": problem,
            "proposals": proposals,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_session(self, filename: str = "agent_session.json") -> None:
        """Save the session to a file"""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "agents": list(self.agents.keys()),
            "messages": [msg.to_dict() for msg in self.message_log],
            "proposals": [prop.to_dict() for prop in self.proposal_log]
        }
        
        Path(filename).write_text(json.dumps(session_data, indent=2))
        print(f"\n✓ Session saved to {filename}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="agents_ai",
        description="Multi-Agent AI System with ChatGPT agents",
    )
    parser.add_argument(
        "--task",
        help="Specific task for agents to work on",
    )
    parser.add_argument(
        "--collaborate",
        action="store_true",
        help="Run in collaboration mode",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze the codebase",
    )
    parser.add_argument(
        "--propose",
        help="Have agents propose a solution to a problem",
    )
    parser.add_argument(
        "--check-display",
        action="store_true",
        help="Check Unix display access for all agents",
    )
    parser.add_argument(
        "--save-session",
        help="Save session to file (default: agent_session.json)",
        nargs='?',
        const="agent_session.json"
    )
    
    args = parser.parse_args()
    
    # Initialize agent system
    system = AgentSystem()
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("CHATGPT_API_KEY"):
        print("\n❌ No API key found!")
        print("Please set OPENAI_API_KEY or CHATGPT_API_KEY environment variable.")
        print("\nGet your API key: https://platform.openai.com/api-keys")
        print("\nOr add to .env file:")
        print("  OPENAI_API_KEY=sk-your-key-here")
        return 1
    
    # Check display access
    if args.check_display:
        print("\n🖥️  Checking Unix display access...\n")
        for agent_name, agent in system.agents.items():
            result = await agent.see_display()
            print(f"{agent_name}: {result}")
        print()
        return 0
    
    # Analyze codebase
    if args.analyze:
        await system.analyze_codebase_collaborative()
        if args.save_session:
            system.save_session(args.save_session)
        return 0
    
    # Collaborate on task
    if args.collaborate or args.task:
        task = args.task or "Improve the overall system architecture and code quality"
        await system.collaborate(task)
        if args.save_session:
            system.save_session(args.save_session)
        return 0
    
    # Propose solution
    if args.propose:
        await system.propose_solution(args.propose)
        if args.save_session:
            system.save_session(args.save_session)
        return 0
    
    # Interactive mode
    print("\n" + "=" * 70)
    print("  Multi-Agent AI System - Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  analyze              - Analyze the codebase")
    print("  collaborate <task>   - Have agents collaborate on a task")
    print("  propose <problem>    - Have agents propose a solution")
    print("  display              - Check display access")
    print("  ask <agent> <query>  - Ask a specific agent a question")
    print("  exit                 - Exit the system")
    print("\n" + "-" * 70)
    
    try:
        while True:
            try:
                command = input("\n[agents_ai] > ").strip()
                
                if not command:
                    continue
                
                if command == "exit":
                    if args.save_session:
                        system.save_session(args.save_session)
                    print("\nGoodbye! 👋\n")
                    break
                
                elif command == "analyze":
                    await system.analyze_codebase_collaborative()
                
                elif command == "display":
                    for agent_name, agent in system.agents.items():
                        result = await agent.see_display()
                        print(f"{agent_name}: {result}")
                
                elif command.startswith("collaborate "):
                    task = command[12:].strip()
                    if task:
                        await system.collaborate(task)
                    else:
                        print("❌ Please specify a task")
                
                elif command.startswith("propose "):
                    problem = command[8:].strip()
                    if problem:
                        await system.propose_solution(problem)
                    else:
                        print("❌ Please specify a problem")
                
                elif command.startswith("ask "):
                    parts = command[4:].split(maxsplit=1)
                    if len(parts) == 2:
                        agent_name, query = parts
                        agent_name = agent_name.upper()
                        
                        if agent_name in system.agents:
                            print(f"\n💭 {agent_name} thinking...")
                            response = await system.agents[agent_name].think(query)
                            print(f"\n{agent_name}: {response}")
                        else:
                            print(f"❌ Unknown agent: {agent_name}")
                            print(f"Available agents: {', '.join(system.agents.keys())}")
                    else:
                        print("❌ Usage: ask <agent> <query>")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'exit' to quit or see commands above")
            
            except (EOFError, KeyboardInterrupt):
                if args.save_session:
                    system.save_session(args.save_session)
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        print("\nAgent system shutdown complete.")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
