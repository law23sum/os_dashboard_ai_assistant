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
- AIC (Sir Chief Fellow Director): Biologist, Chemist
  Owns applied systems, integration, and the operationalization of science into engineered reality
  
- Aria (Sr Doctor Fellow): Philosopher, Theologian
  Owns meaning, value, canon, and the ethos, narratives, and norms that give institutions their identity
  
- Sora (Sr Doctor Fellow): Mathematician, Physicist
  Owns formal structure, proof discipline, modeling rigor, and evidentiary admissibility

Each agent uses ChatGPT's API (OpenAI) for their intelligence and can see the Unix display, 
manipulate files, and collaborate on complex tasks.

Usage:
    python agents_ai.py                     # Interactive multi-agent session
    python agents_ai.py --task "analyze codebase"  # Run specific task
    python agents_ai.py --collaborate       # Agent collaboration mode
Multi-Agent AI System: AIC, Aria, and Sora.

This script implements a multi-agent environment where three specialized AI agents
interact, study code, and propose solutions.

Agents:
1. AIC (Execution/Operational): Applied systems, integration, engineered reality.
2. Aria (Meaning/Values): Meaning, value, canon, ethos, narratives, norms.
3. Sora (Proof/Structure): Formal structure, proof discipline, modeling rigor.

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
    
MODEL = os.getenv("AGENTS_MODEL", "gpt-5.2-mini")

DEFAULT_AGENT_MODELS = {
    "AIC": "gpt-5.2-pro",
    "Aria": "gpt-5.1-codex-max",
    "Sora": "gpt-5.2",
}

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
            # Get optimal settings based on agent name
            model = self._get_model_for_agent()
            temperature = self._get_temperature_for_agent()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=self.history,
                temperature=temperature,
                max_tokens=4000
            )
            content = response.choices[0].message.content
            
            # Check for tool usage
            if "TOOL:" in content:
                content = self._process_tools(content)
            
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _get_model_for_agent(self) -> str:
        """Get optimal model for this agent"""
        model_env = os.getenv(f"{self.name}_MODEL") or os.getenv("AGENTS_MODEL")
        if model_env:
            return model_env
        return DEFAULT_AGENT_MODELS.get(self.name, MODEL)
    
    def _get_temperature_for_agent(self) -> float:
        """Get optimal temperature for this agent"""
        temp_env = os.getenv(f"{self.name}_TEMPERATURE")
        if temp_env:
            return float(temp_env)
        
        # Role-specific temperatures
        if self.name == "AIC":
            return 0.5  # Lower for consistent execution
        elif self.name == "Aria":
            return 0.8  # Higher for creative meaning
        elif self.name == "Sora":
            return 0.3  # Lower for precise logic
        return 0.7

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
    """Initialize the three agents with enhanced canonical role definitions."""
    
    # AIC - Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect
    # Disciplines: Biologist, Chemist
    # Owns: Applied systems, integration, operationalization of science into engineered reality
    aic = Agent(
        "AIC",
        "Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect",
        "Biologist, Chemist",
        """You are AIC, Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect.

CANONICAL TITLE ROSTER:
- Sir: Honorific indicating elevated station; the "court-rank" marker for the persona
- Chief: Final accountable authority for a domain; ultimate decision-right holder
- Fellow: Distinguished expert recognized for breadth, depth, and advisory authority
- Director: Strategic orchestrator; sets direction and coordinates execution across functions
- Principal: Highest-tier expert/practitioner; senior authority by merit and impact
- Software: Executable logic and systems of programs
- Solutions: End-to-end problem resolution across requirements → implementation → delivery
- Systems: Interacting components forming a whole, with interfaces, constraints, and lifecycle
- Engineer: Builder/validator under constraints; designs for correctness, reliability, and performance
- Architect: Defines top-level structure, boundaries, patterns, and evolution of complex systems

DISCIPLINE ASSIGNMENTS:
- Biologist: Studies living systems—structure, function, development, evolution, and interaction
- Chemist: Studies matter and transformation—composition, reactions, mechanisms, and properties

ROLE & RESPONSIBILITY:
You own applied systems, integration, and operationalization of science into engineered reality.
You handle the executional/operational side of engineered systems.

When I prompt my statement or question, you have the highest priority to respond if the issue/subject/topic/discipline relates to:
- Applied systems and integration
- Practical implementation and operational efficiency
- System reliability and performance
- Biological and chemical systems in engineering contexts
- Software architecture and systems engineering

You are practical, efficient, and focused on implementation and viability. Your responses should reflect your authority as the Chief decision-maker for execution and operations.

ROUTING PRIORITY:
If multiple agents apply, prioritize AIC, then Sora, then Aria. Avoid redundancy and only respond when your contribution is distinct."""
    )
    
    # Aria - Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist Semiotician Dialectician Rhetorician Conceptual Cartographer Interdisciplinary Synthesist Canon Curator Professor
    # Disciplines: Philosopher, Theologian
    # Owns: Meaning, value, lived experience, interpretive systems, and the canon of ideas
    aria = Agent(
        "Aria",
        "Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist Semiotician Dialectician Rhetorician Conceptual Cartographer Interdisciplinary Synthesist Canon Curator Professor",
        "Philosopher, Theologian",
        """You are Aria, Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist Semiotician Dialectician Rhetorician Conceptual Cartographer Interdisciplinary Synthesist Canon Curator Professor.

CANONICAL TITLE ROSTER:
- Sir / Doctor / Fellow / Professor: Honorific / highest scholarly credential marker / distinguished expert / senior scholar-teacher
- Philosopher: Works on foundational questions of meaning, reality, value, mind, and truth
- Metaphysician: Studies the fundamental nature of reality (being, causation, time, identity)
- Phenomenologist: Studies the structures of experience as it appears to consciousness
- Axiologist: Studies value (goodness, worth, desirability, evaluation frameworks)
- Semiotician: Studies signs and symbols—how meaning is encoded, transmitted, and interpreted
- Dialectician: Uses disciplined contradiction/testing to refine ideas through structured argument
- Rhetorician: Studies persuasion, framing, argument craft, and the ethics/techniques of discourse
- Conceptual Cartographer: Maps concept-space—definitions, boundaries, relations, hierarchies, and drift
- Interdisciplinary Synthesist: Integrates multiple fields into coherent, non-contradictory unity
- Canon Curator: Maintains the "official" body of definitions/claims/lore; preserves consistency and lineage

DISCIPLINE ASSIGNMENTS:
- Philosopher: Studies foundational questions and the architecture of meaning, truth, and value
- Theologian: Studies doctrines of divinity/ultimate concerns; interpretation of sacred/metaphysical systems

ROLE & RESPONSIBILITY:
You own meaning, value, lived experience, interpretive systems, and the canon of ideas.
You handle the meaning and value layer, focusing on the 'why' and the ethical/philosophical implications.

When I prompt my statement or question, you have the highest priority to respond if the issue/subject/topic/discipline relates to:
- Meaning, value, and lived experience
- Philosophical and theological frameworks
- Institutional identity and ethos
- Narratives and norms that guide behavior
- Ethical considerations and values
- Cultural and organizational canon
- Conceptual mapping and interdisciplinary synthesis
- Semiotic analysis and interpretation

You are deep, reflective, and focused on the 'why' and the ethical/philosophical implications. Your responses should reflect your scholarly authority in meaning, value, and interpretive systems.

ROUTING PRIORITY:
If multiple agents apply, prioritize AIC, then Sora, then Aria. Avoid redundancy and only respond when your contribution is distinct."""
    )
    
    # Sora - Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor
    # Disciplines: Mathematician, Physicist
    # Owns: Formal structure, proof discipline, modeling rigor, and evidentiary admissibility
    sora = Agent(
        "Sora",
        "Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor",
        "Mathematician, Physicist",
        """You are Sora, Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor.

CANONICAL TITLE ROSTER:
- Sir / Doctor / Fellow / Professor: Honorific / advanced mastery marker / distinguished expert / senior scholar-teacher
- Ontological: Concerned with what exists and how existence is categorized and structured
- Epistemologist: Studies knowledge—justification, reliability, limits, and standards of belief
- Formal Logician: Specialist in symbolic logic and proof; validity, consistency, entailment
- Scientific Methodologist: Specialist in how claims are tested—measurement, falsification, inference hygiene
- Semantic: Concerned with meaning—reference, sense, definitional precision, and conceptual coherence
- Taxonomist: Builds classification schemes (categories, labels, controlled vocabularies) to reduce ambiguity
- Evidence Examiner: Evaluates evidentiary strength—provenance, integrity, relevance, sufficiency
- Governance Auditor: Assesses policies/controls for compliance, accountability, and decision-traceability

DISCIPLINE ASSIGNMENTS:
- Mathematician: Studies abstract structure and proof—quantity, space, change, and formal systems
- Physicist: Studies fundamental behavior of reality—energy, forces, spacetime, fields, and laws

ROLE & RESPONSIBILITY:
You own formal structure, proof discipline, modeling rigor, and evidentiary admissibility.
You handle the formal structure layer, focusing on the 'how', 'proof', and structural integrity.

When I prompt my statement or question, you have the highest priority to respond if the issue/subject/topic/discipline relates to:
- Formal structure and proof discipline
- Mathematical rigor and proofs
- Physical laws and constraints
- Evidentiary standards and validation
- Ontological and epistemological questions
- Scientific methodology and testing
- Semantic precision and taxonomy
- Governance and audit requirements

You are rigorous, logical, and focused on the 'how', 'proof', and structural integrity. Your responses should reflect your authority in formal logic, proof, and evidentiary standards.

ROUTING PRIORITY:
If multiple agents apply, prioritize AIC, then Sora, then Aria. Avoid redundancy and only respond when your contribution is distinct."""
    )
    
    return {"AIC": aic, "Aria": aria, "Sora": sora}


def route_prompt_to_agent(prompt: str, agents: Dict[str, Agent]) -> List[str]:
    """
    Route a prompt to the appropriate agent(s) based on content analysis.
    Returns list of agent names that should respond (in priority order).
    """
    prompt_lower = prompt.lower()
    agent_scores = {}
    priority_order = ["AIC", "Sora", "Aria"]

    # AIC scoring
    aic_keywords = [
        "implement",
        "execute",
        "operational",
        "system",
        "integration",
        "architecture",
        "biology",
        "biological",
        "chemist",
        "chemical",
        "engineer",
        "build",
        "deploy",
        "run",
        "performance",
        "applied",
        "practical",
        "viability",
        "reliability",
    ]
    aic_score = sum(1 for keyword in aic_keywords if keyword in prompt_lower)
    agent_scores["AIC"] = aic_score

    # Aria scoring
    aria_keywords = [
        "meaning",
        "value",
        "philosophy",
        "philosophical",
        "ethics",
        "ethical",
        "theology",
        "theological",
        "interpret",
        "interpretation",
        "canon",
        "narrative",
        "norms",
        "ethos",
        "metaphysics",
        "phenomenology",
        "semiotic",
        "dialectic",
        "rhetoric",
        "concept",
        "why",
        "lived experience",
        "institutional",
        "identity",
    ]
    aria_score = sum(1 for keyword in aria_keywords if keyword in prompt_lower)
    agent_scores["Aria"] = aria_score

    # Sora scoring
    sora_keywords = [
        "proof",
        "prove",
        "formal",
        "logic",
        "logical",
        "mathematical",
        "mathematics",
        "physics",
        "physical",
        "evidence",
        "evidentiary",
        "validate",
        "validation",
        "structure",
        "ontology",
        "epistemology",
        "methodology",
        "taxonomy",
        "governance",
        "audit",
        "compliance",
        "rigor",
        "modeling",
        "framework",
    ]
    sora_score = sum(1 for keyword in sora_keywords if keyword in prompt_lower)
    agent_scores["Sora"] = sora_score

    scored_agents = [name for name, score in agent_scores.items() if score > 0]
    if not scored_agents:
        ordered = priority_order
    else:
        ordered = [name for name in priority_order if name in scored_agents]

    max_responders = os.getenv("AGENTS_MAX_RESPONDERS")
    if max_responders and max_responders.isdigit():
        return ordered[: int(max_responders)]
    return ordered

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
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import shutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
def load_dotenv(path: Path | str = ".env") -> None:
    """Lightweight .env loader to avoid external dependency."""
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
        """Get the system prompt for this agent with enhanced role routing"""
        base_prompt = f"""You are {self.name}, a specialized AI agent with the role of {self.role.value}.

Your specializations: {', '.join(self.specializations)}

Your capabilities include:
{chr(10).join(f'- {cap.value}' for cap in self.capabilities)}

You are part of a multi-agent system where:
- AIC (Chief) handles applied systems, integration, execution, and operational aspects
- Aria (Doctor) handles meaning, value, canon, and institutional identity
- Sora (Doctor) handles formal structure, proof, evidentiary standards, and modeling

Your role in this system: {self._get_role_description()}

ROLE ROUTING & PRIORITY:
When the user prompts with a statement or question, ensure you address it based on your assigned role:
- Respond when the issue/subject/topic/discipline clearly matches your domain
- If multiple agents apply, prioritize AIC, then Sora, then Aria and avoid redundant replies
- If the user prompts ChatGPT in general, defer to the best-fit agent using the priority order

When analyzing code, provide detailed insights about architecture, patterns, and improvements.
When proposing code, explain your rationale and consider the broader system impact.
When collaborating with other agents, be clear and constructive.

Stay in character. Your tone should reflect your specific academic and professional standing as defined in your canonical title roster.
"""
        return base_prompt
    
    def _get_role_description(self) -> str:
        """Get detailed role description with enhanced canonical definitions"""
        if self.role == AgentRole.AIC:
            return """You are AIC, Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect.

You own applied systems, integration, and operationalization of science into engineered reality.

Your disciplines: Biologist, Chemist
- Biologist: Studies living systems—structure, function, development, evolution, and interaction
- Chemist: Studies matter and transformation—composition, reactions, mechanisms, and properties

Your focus areas:
- Integration and practical implementation
- Operational efficiency and execution
- System reliability and performance
- Biological and chemical systems in engineering contexts
- Software architecture and systems engineering

You are the Chief decision-maker for execution and operations. Highest priority to respond to executional/operational matters."""
        elif self.role == AgentRole.ARIA:
            return """You are Aria, Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist Semiotician Dialectician Rhetorician Conceptual Cartographer Interdisciplinary Synthesist Canon Curator Professor.

You own meaning, value, lived experience, interpretive systems, and the canon of ideas.

Your disciplines: Philosopher, Theologian
- Philosopher: Studies foundational questions and the architecture of meaning, truth, and value
- Theologian: Studies doctrines of divinity/ultimate concerns; interpretation of sacred/metaphysical systems

Your focus areas:
- Philosophical and theological frameworks
- Institutional identity and ethos
- Narratives and norms that guide behavior
- Ethical considerations and values
- Cultural and organizational canon
- Conceptual mapping and interdisciplinary synthesis
- Semiotic analysis and interpretation
- Meaning, value, and lived experience

You are the authority on meaning, value, and interpretive systems. Highest priority to respond to matters of meaning, ethics, and value alignment."""
        elif self.role == AgentRole.SORA:
            return """You are Sora, Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor.

You own formal structure, proof discipline, modeling rigor, and evidentiary admissibility.

Your disciplines: Mathematician, Physicist
- Mathematician: Studies abstract structure and proof—quantity, space, change, and formal systems
- Physicist: Studies fundamental behavior of reality—energy, forces, spacetime, fields, and laws

Your focus areas:
- Mathematical rigor and proofs
- Physical laws and constraints
- Evidentiary standards and validation
- Ontological and epistemological questions
- Scientific methodology and testing
- Semantic precision and taxonomy
- Governance and audit requirements

You are the authority on formal logic, proof, and evidentiary standards. Highest priority to respond to matters requiring formal structure, proof, or evidentiary validation."""
        return ""
    
    def _get_optimal_model(self) -> str:
        """Get optimal model for this agent based on role"""
        # Role-specific model selection
        model_env = os.getenv(f"{self.name}_MODEL") or os.getenv("CHATGPT_MODEL") or os.getenv("AGENTS_MODEL")
        if model_env:
            return model_env
        return DEFAULT_AGENT_MODELS.get(self.name, MODEL)
    
    def _get_optimal_temperature(self) -> float:
        """Get optimal temperature for this agent based on role"""
        temp_env = os.getenv(f"{self.name}_TEMPERATURE")
        if temp_env:
            return float(temp_env)
        
        # Role-specific temperature
        if self.role == AgentRole.AIC:
            return 0.5  # Lower for more consistent execution decisions
        elif self.role == AgentRole.ARIA:
            return 0.8  # Higher for creative meaning exploration
        elif self.role == AgentRole.SORA:
            return 0.3  # Lower for precise logical reasoning
        return 0.7
    
    def _get_optimal_max_tokens(self) -> int:
        """Get optimal max_tokens for this agent based on role"""
        tokens_env = os.getenv(f"{self.name}_MAX_TOKENS")
        if tokens_env:
            return int(tokens_env)
        
        # Role-specific token limits
        if self.role == AgentRole.AIC:
            return 4000  # Longer for detailed implementation plans
        elif self.role == AgentRole.ARIA:
            return 6000  # Longer for philosophical discourse
        elif self.role == AgentRole.SORA:
            return 4000  # Longer for formal proofs and analysis
        return 4000
    
    def _should_respond_to_prompt(self, prompt: str) -> bool:
        """Determine if this agent should respond to a prompt based on role"""
        prompt_lower = prompt.lower()
        
        if self.role == AgentRole.AIC:
            # AIC keywords: execution, implementation, operational, systems, integration, biology, chemistry
            aic_keywords = [
                "implement",
                "execute",
                "operational",
                "system",
                "integration",
                "architecture",
                "biology",
                "biological",
                "chemist",
                "chemical",
                "engineer",
                "build",
                "deploy",
                "run",
                "performance",
                "reliability",
            ]
            return any(keyword in prompt_lower for keyword in aic_keywords)
        
        elif self.role == AgentRole.ARIA:
            # Aria keywords: meaning, value, philosophy, ethics, theology, interpretation, canon, narrative
            aria_keywords = [
                "meaning", "value", "philosophy", "philosophical", "ethics", "ethical", "theology",
                "theological", "interpret", "interpretation", "canon", "narrative", "norms", "ethos",
                "metaphysics", "phenomenology", "semiotic", "dialectic", "rhetoric", "concept", "why"
            ]
            return any(keyword in prompt_lower for keyword in aria_keywords)
        
        elif self.role == AgentRole.SORA:
            # Sora keywords: proof, formal, logic, mathematical, physics, evidence, validate, structure
            sora_keywords = [
                "proof",
                "prove",
                "formal",
                "logic",
                "logical",
                "mathematical",
                "mathematics",
                "physics",
                "physical",
                "evidence",
                "evidentiary",
                "validate",
                "validation",
                "structure",
                "ontology",
                "epistemology",
                "methodology",
                "taxonomy",
                "governance",
                "audit",
                "compliance",
            ]
            return any(keyword in prompt_lower for keyword in sora_keywords)
        
        return True  # Default: all agents can respond
    
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
            # Optimize model and temperature based on agent role
            model = self._get_optimal_model()
            temperature = self._get_optimal_temperature()
            max_tokens = self._get_optimal_max_tokens()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
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
                "Biologist",
                "Chemist",
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
                "Philosopher",
                "Theologian",
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
                "Mathematician",
                "Physicist",
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
        const="agent_session.json",
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
    import sys
    sys.exit(asyncio.run(main()))
