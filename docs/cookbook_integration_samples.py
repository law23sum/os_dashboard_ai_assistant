"""
OpenAI Cookbook Integration Samples
Ready-to-use code patterns for OS Dashboard AI Assistant

Source: https://github.com/openai/openai-cookbook (MIT License)
Adapted for OS Dashboard AI Assistant Technical Spec V6

License Notice:
This file contains code patterns derived from the OpenAI Cookbook,
licensed under the MIT License. See ACKNOWLEDGMENTS.md for full attribution.
"""

from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import subprocess
import asyncio
import json
import numpy as np
from pydantic import BaseModel
from openai import OpenAI


# =============================================================================
# 1. AGENT ORCHESTRATION FRAMEWORK (Spec Section 0.5, 4.1-4.3)
# Source: examples/Orchestrating_agents.ipynb
# =============================================================================

class AgentRole(str, Enum):
    """Agent roles matching OS Dashboard personas"""
    CHRIS = "chris"  # Owner archetype
    AIC = "aic"      # Meta-governor
    SORA = "sora"    # Strategic architect
    ARIA = "aria"    # Emotional/symbolic muse
    CUSTOM = "custom"


class Agent(BaseModel):
    """Cognitive agent/persona definition"""
    name: str
    role: AgentRole
    instructions: str
    tools: List[str] = []
    handoff_agents: List[str] = []
    
    def to_system_message(self) -> str:
        """Convert agent config to system message"""
        return f"""You are {self.name}, a {self.role.value} agent.

{self.instructions}

Available tools: {', '.join(self.tools)}
Can hand off to: {', '.join(self.handoff_agents)}"""


class AgentOrchestrator:
    """
    Multi-agent orchestration system
    Implements persona coordination from Tech Spec Section 0.5
    """
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
        self.agents: Dict[str, Agent] = {}
        self.conversation_history: List[Dict] = []
        self.active_agent: Optional[str] = None
    
    def register_agent(self, agent: Agent):
        """Register agent/persona to orchestrator"""
        self.agents[agent.name] = agent
    
    def execute_with_agent(
        self,
        agent_name: str,
        user_message: str,
        max_iterations: int = 5
    ) -> Dict:
        """
        Execute task with specific agent, handling handoffs
        
        Returns:
            Dict with response, final_agent, and execution_trace
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not registered")
        
        current_agent = agent_name
        execution_trace = []
        
        for iteration in range(max_iterations):
            agent = self.agents[current_agent]
            
            # Prepare messages
            messages = [
                {"role": "system", "content": agent.to_system_message()},
                {"role": "user", "content": user_message}
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history[-5:])  # Last 5 messages
            
            # Execute
            response = self.client.chat.completions.create(
                model="gpt-5.1",
                messages=messages
            )
            
            result = response.choices[0].message.content
            
            execution_trace.append({
                "agent": current_agent,
                "iteration": iteration,
                "response": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Check for handoff in response
            handoff_agent = self._detect_handoff(result, agent.handoff_agents)
            
            if handoff_agent:
                current_agent = handoff_agent
                user_message = f"Previous context from {agent.name}: {result}"
            else:
                # Task complete
                break
        
        return {
            "response": result,
            "final_agent": current_agent,
            "execution_trace": execution_trace,
            "iterations": len(execution_trace)
        }
    
    def _detect_handoff(self, response: str, handoff_agents: List[str]) -> Optional[str]:
        """Detect if response indicates handoff to another agent"""
        response_lower = response.lower()
        for agent_name in handoff_agents:
            if f"hand off to {agent_name.lower()}" in response_lower:
                return agent_name
            if f"transfer to {agent_name.lower()}" in response_lower:
                return agent_name
        return None


# =============================================================================
# 2. MCP (MODEL CONTEXT PROTOCOL) INTEGRATION (Spec Section 5.6, 9.2)
# Source: examples/mcp/mcp_tool_guide.ipynb
# =============================================================================

class MCPDriver(BaseModel):
    """MCP server configuration for driver integration"""
    driver_id: str
    server_url: str
    api_key: str
    allowed_tools: List[str] = ["*"]  # "*" for all tools
    description: str = ""


class MCPDriverManager:
    """
    Manages MCP-based drivers for external service integration
    Implements Software & SaaS Drivers from Tech Spec Section 5.6
    """
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
        self.registered_drivers: Dict[str, MCPDriver] = {}
    
    def register_driver(self, driver: MCPDriver):
        """Register MCP driver"""
        self.registered_drivers[driver.driver_id] = driver
    
    def execute_with_drivers(
        self,
        task: str,
        driver_ids: List[str],
        instructions: Optional[str] = None
    ) -> Dict:
        """
        Execute task using specified MCP drivers
        
        Args:
            task: Task description
            driver_ids: List of driver IDs to make available
            instructions: Optional system instructions
        
        Returns:
            Dict with response and driver execution log
        """
        # Build MCP tools configuration
        mcp_tools = []
        for driver_id in driver_ids:
            if driver_id not in self.registered_drivers:
                raise ValueError(f"Driver {driver_id} not registered")
            
            driver = self.registered_drivers[driver_id]
            mcp_tools.append({
                "type": "mcp",
                "mcp": {
                    "server_url": driver.server_url,
                    "headers": {
                        "Authorization": f"Bearer {driver.api_key}"
                    },
                    "allowed_tools": driver.allowed_tools
                }
            })
        
        # Execute with MCP drivers
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": task})
        
        response = self.client.responses.create(
            model="gpt-5.1",
            tools=mcp_tools,
            messages=messages
        )
        
        # Extract driver execution log
        driver_log = []
        for item in response.items:
            if item.type == "mcp_tool_call":
                driver_log.append({
                    "driver": item.mcp_tool_call.server_url,
                    "tool": item.mcp_tool_call.tool_name,
                    "arguments": item.mcp_tool_call.arguments,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return {
            "response": response.choices[0].message.content,
            "driver_log": driver_log,
            "total_driver_calls": len(driver_log)
        }


# =============================================================================
# 3. SANDBOXED CODE EXECUTION (Spec Section 5.11, 8.5)
# Source: examples/Build_a_coding_agent_with_GPT-5.1.ipynb
# =============================================================================

class ExecutionResult(BaseModel):
    """Result of command execution"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: Optional[int] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class SandboxedExecutor:
    """
    Sandboxed command execution environment
    Implements Sandbox & Testbed Spawner from Tech Spec Section 5.11
    
    WARNING: In production, use container/VM isolation (Docker, Firecracker, etc.)
    This basic implementation uses filesystem isolation only.
    """
    def __init__(self, workspace_dir: str, allowed_commands: Optional[List[str]] = None):
        self.workspace = Path(workspace_dir).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Command whitelist for safety
        self.allowed_commands = allowed_commands or [
            "python", "pip", "npm", "node", "git",
            "ls", "cat", "echo", "mkdir", "touch"
        ]
        
        self.execution_log: List[Dict] = []
    
    def execute_command(
        self,
        command: str,
        timeout: int = 30,
        env_vars: Optional[Dict[str, str]] = None,
        require_approval: bool = True
    ) -> ExecutionResult:
        """
        Execute shell command with safety constraints
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds
            env_vars: Additional environment variables
            require_approval: If True, requires explicit approval before execution
        
        Returns:
            ExecutionResult with stdout, stderr, and success status
        """
        import time
        
        # Validate command
        if not self._is_command_allowed(command):
            return ExecutionResult(
                success=False,
                error=f"Command not allowed: {command}"
            )
        
        if require_approval:
            # In production, implement proper approval workflow
            print(f"[APPROVAL REQUIRED] Execute: {command}")
            # approval = input("Approve? (y/n): ")
            # if approval.lower() != 'y':
            #     return ExecutionResult(success=False, error="Execution not approved")
        
        try:
            # Set up isolated environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Restrict to workspace
            env['PWD'] = str(self.workspace)
            
            start_time = time.time()
            
            # Execute with timeout and directory constraint
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Log execution
            log_entry = {
                "command": command,
                "returncode": result.returncode,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.execution_log.append(log_entry)
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Command timeout exceeded ({timeout}s)"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is in whitelist"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        base_command = cmd_parts[0]
        return base_command in self.allowed_commands
    
    def apply_patch(self, file_path: str, content: str) -> ExecutionResult:
        """
        Write/update file in workspace
        
        Args:
            file_path: Relative path within workspace
            content: File content
        
        Returns:
            ExecutionResult indicating success/failure
        """
        try:
            target = self.workspace / file_path
            
            # Ensure path is within workspace (security check)
            if not target.resolve().is_relative_to(self.workspace):
                return ExecutionResult(
                    success=False,
                    error="Path escape attempt detected"
                )
            
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            
            self.execution_log.append({
                "operation": "apply_patch",
                "file": file_path,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return ExecutionResult(
                success=True,
                stdout=f"File written: {file_path}"
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"File write error: {str(e)}"
            )
    
    def get_execution_log(self) -> List[Dict]:
        """Get audit log of all executions"""
        return self.execution_log


# =============================================================================
# 4. RAG WITH AUDIT TRAIL (Spec Section 6.2, 6.5, 11.5)
# Source: examples/Question_answering_using_embeddings.ipynb
# =============================================================================

class Document(BaseModel):
    """Document with metadata for CIR store"""
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class AuditableRAG:
    """
    RAG system with full audit trail
    Implements CIR Store, Search Services, and Record Auditor
    from Tech Spec Sections 6.2, 6.5, 11.5
    """
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
        self.documents: Dict[str, Document] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.audit_log: List[Dict] = []
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to CIR store with embeddings
        
        Args:
            documents: List of Document objects to index
        """
        # Generate embeddings
        contents = [doc.content for doc in documents]
        
        response = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=contents
        )
        
        # Store documents with embeddings
        for doc, embedding_obj in zip(documents, response.data):
            doc.embedding = embedding_obj.embedding
            self.documents[doc.id] = doc
        
        # Update embeddings matrix
        self._rebuild_embeddings_matrix()
        
        # Audit log
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "operation": "add_documents",
            "document_count": len(documents),
            "model": "text-embedding-3-large"
        })
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search with provenance tracking
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of search results with similarity scores and provenance
        """
        if not self.documents:
            return []
        
        # Get query embedding
        query_response = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=[query]
        )
        query_embedding = np.array(query_response.data[0].embedding)
        
        # Compute similarities
        similarities = np.dot(self.embeddings_matrix, query_embedding)
        
        # Apply metadata filters
        doc_list = list(self.documents.values())
        if filter_metadata:
            filtered_indices = [
                i for i, doc in enumerate(doc_list)
                if all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
            ]
            similarities = similarities[filtered_indices]
            doc_list = [doc_list[i] for i in filtered_indices]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            {
                "document_id": doc_list[i].id,
                "content": doc_list[i].content,
                "metadata": doc_list[i].metadata,
                "similarity": float(similarities[i]),
                "rank": rank
            }
            for rank, i in enumerate(top_indices)
        ]
        
        # Audit log
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "operation": "semantic_search",
            "query": query,
            "results_count": len(results),
            "top_similarity": results[0]["similarity"] if results else 0.0,
            "filter": filter_metadata
        })
        
        return results
    
    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        system_instructions: Optional[str] = None
    ) -> Dict:
        """
        Generate answer with full provenance
        
        Args:
            question: User question
            top_k: Number of context documents to retrieve
            system_instructions: Optional system instructions
        
        Returns:
            Dict with answer, sources, and audit_id
        """
        # Search for relevant context
        relevant_docs = self.semantic_search(question, top_k=top_k)
        
        if not relevant_docs:
            return {
                "answer": "No relevant documents found.",
                "sources": [],
                "audit_id": None
            }
        
        # Build context
        context = "\n\n".join([
            f"[Document {i+1}]:\n{doc['content']}"
            for i, doc in enumerate(relevant_docs)
        ])
        
        # Generate answer
        messages = []
        if system_instructions:
            messages.append({"role": "system", "content": system_instructions})
        else:
            messages.append({
                "role": "system",
                "content": "Answer the question based solely on the provided context. Cite document numbers when referencing information."
            })
        
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        })
        
        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        # Complete audit record
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": "answer_question",
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "document_id": doc["document_id"],
                    "content_preview": doc["content"][:200],
                    "similarity": doc["similarity"]
                }
                for doc in relevant_docs
            ],
            "model": "gpt-5.1",
            "tokens": response.usage.dict()
        }
        self.audit_log.append(audit_entry)
        
        return {
            "answer": answer,
            "sources": relevant_docs,
            "audit_id": len(self.audit_log) - 1,
            "provenance": audit_entry
        }
    
    def _rebuild_embeddings_matrix(self):
        """Rebuild numpy matrix from document embeddings"""
        if not self.documents:
            self.embeddings_matrix = None
            return
        
        embeddings = [doc.embedding for doc in self.documents.values()]
        self.embeddings_matrix = np.array(embeddings)
    
    def generate_evidence_pack(self, audit_id: Optional[int] = None) -> Dict:
        """
        Generate evidence pack for regulator/auditor
        Implements Evidence Pack Generator from Tech Spec Section 11.7
        
        Args:
            audit_id: Specific audit entry ID, or None for full trail
        
        Returns:
            Dict with audit trail and metadata
        """
        if audit_id is not None:
            if audit_id >= len(self.audit_log):
                raise ValueError(f"Invalid audit_id: {audit_id}")
            return {
                "evidence_pack_type": "single_operation",
                "audit_entry": self.audit_log[audit_id],
                "generated_at": datetime.utcnow().isoformat()
            }
        
        return {
            "evidence_pack_type": "complete_trail",
            "audit_trail": self.audit_log,
            "total_operations": len(self.audit_log),
            "document_count": len(self.documents),
            "generated_at": datetime.utcnow().isoformat()
        }


# =============================================================================
# 5. STRUCTURED CAPSULE METADATA (Spec Section 8.2)
# Source: examples/Structured_Outputs_Intro.ipynb
# =============================================================================

class CapsuleType(str, Enum):
    """Capsule taxonomy from Tech Spec Section 8.1"""
    TEMPLATE = "template"
    ANALYTICAL = "analytical"
    EXECUTABLE = "executable"
    INFRA = "infra"
    COMPOSITE = "composite"
    TEST = "test"


class DriverDependency(BaseModel):
    """Driver requirement for capsule"""
    driver_id: str
    driver_type: str
    version: str
    required: bool = True
    configuration: Dict[str, Any] = {}


class EnvironmentSpec(BaseModel):
    """Environment requirements"""
    os_type: str  # "linux", "macos", "windows"
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    packages: List[str] = []
    environment_variables: Dict[str, str] = {}


class TestCase(BaseModel):
    """Test specification"""
    test_id: str
    description: str
    expected_outcome: str
    assertion_type: str  # "exit_code", "output_contains", "file_exists", etc.


class CapsuleMetadata(BaseModel):
    """
    Structured capsule metadata
    Implements Capsule Structure & Metadata from Tech Spec Section 8.2
    """
    capsule_id: str
    name: str
    description: str
    capsule_type: CapsuleType
    version: str
    author: str
    created_at: str
    
    # Dependencies
    driver_dependencies: List[DriverDependency]
    environment_spec: EnvironmentSpec
    
    # Execution
    entrypoint: str
    execution_timeout: int = 300  # seconds
    
    # Testing
    test_cases: List[TestCase] = []
    
    # Constraints
    requires_approval: bool = True
    allowed_operations: List[str] = []
    resource_limits: Dict[str, Any] = {}
    
    # Metadata
    tags: List[str] = []
    documentation_url: Optional[str] = None


class CapsuleMetadataGenerator:
    """Generate structured capsule metadata using LLM"""
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
    
    def generate_metadata(
        self,
        description: str,
        source_code: Optional[str] = None,
        existing_metadata: Optional[Dict] = None
    ) -> CapsuleMetadata:
        """
        Extract capsule metadata using structured outputs
        
        Args:
            description: Capsule description
            source_code: Optional source code to analyze
            existing_metadata: Optional partial metadata to complete
        
        Returns:
            Complete CapsuleMetadata object
        """
        prompt = f"""Analyze the following capsule and generate complete metadata:

Description: {description}
"""
        if source_code:
            prompt += f"\nSource Code:\n```\n{source_code[:2000]}\n```"
        
        if existing_metadata:
            prompt += f"\nExisting Metadata:\n{json.dumps(existing_metadata, indent=2)}"
        
        prompt += """

Generate complete capsule metadata including:
- Appropriate capsule type
- All driver dependencies with versions
- Complete environment specifications
- Test cases for validation
- Resource limits and constraints
- Relevant tags for categorization
"""
        
        response = self.client.beta.chat.completions.parse(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing code and workflows to generate structured capsule metadata for the OS Dashboard system."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=CapsuleMetadata
        )
        
        return response.choices[0].message.parsed


# =============================================================================
# 6. MULTI-AGENT COLLABORATION (Spec Section 7.12)
# Source: examples/agents_sdk/multi-agent-portfolio-collaboration/
# =============================================================================

class CollaborativeWorkspace:
    """
    Multi-agent collaboration workspace
    Implements Multi-User Projects & Collaboration from Tech Spec Section 7.12
    """
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.client = OpenAI()
        self.agents: Dict[str, Agent] = {}
        self.shared_state: Dict[str, Any] = {}
        self.ledger: List[Dict] = []  # Project ledger (Tech Spec 3.7)
    
    def register_agent(self, agent: Agent):
        """Register agent to workspace"""
        self.agents[agent.name] = agent
        self._log_event({
            "event_type": "agent_registered",
            "agent": agent.name,
            "role": agent.role.value
        })
    
    async def execute_collaborative_task(
        self,
        task: str,
        required_agents: List[str],
        execution_mode: str = "parallel"  # "parallel" or "sequential"
    ) -> Dict:
        """
        Execute task with multiple agents
        
        Args:
            task: Task description
            required_agents: List of agent names to involve
            execution_mode: "parallel" for concurrent, "sequential" for ordered
        
        Returns:
            Dict with consolidated results and execution trace
        """
        if execution_mode == "parallel":
            return await self._execute_parallel(task, required_agents)
        else:
            return await self._execute_sequential(task, required_agents)
    
    async def _execute_parallel(
        self,
        task: str,
        required_agents: List[str]
    ) -> Dict:
        """Execute agents in parallel"""
        tasks = []
        for agent_name in required_agents:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not registered")
            tasks.append(self._execute_agent_subtask(agent_name, task))
        
        # Execute all agents concurrently
        agent_results = await asyncio.gather(*tasks)
        
        # Log results
        results = {}
        for agent_name, result in zip(required_agents, agent_results):
            results[agent_name] = result
            self._log_event({
                "event_type": "agent_completed",
                "agent": agent_name,
                "task": task
            })
        
        # Synthesize final result
        final_result = await self._synthesize_results(results, task)
        
        return {
            "workspace_id": self.workspace_id,
            "task": task,
            "execution_mode": "parallel",
            "agent_results": results,
            "final_result": final_result,
            "ledger_entries": len(self.ledger)
        }
    
    async def _execute_sequential(
        self,
        task: str,
        required_agents: List[str]
    ) -> Dict:
        """Execute agents in sequence, passing context"""
        results = {}
        context = task
        
        for agent_name in required_agents:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not registered")
            
            result = await self._execute_agent_subtask(agent_name, context)
            results[agent_name] = result
            
            # Pass result as context to next agent
            context = f"Previous work by {agent_name}:\n{result['output']}\n\nContinue with: {task}"
            
            self._log_event({
                "event_type": "agent_completed",
                "agent": agent_name,
                "task": task
            })
        
        # Final result is last agent's output
        final_result = results[required_agents[-1]]["output"]
        
        return {
            "workspace_id": self.workspace_id,
            "task": task,
            "execution_mode": "sequential",
            "agent_results": results,
            "final_result": final_result,
            "ledger_entries": len(self.ledger)
        }
    
    async def _execute_agent_subtask(
        self,
        agent_name: str,
        task: str
    ) -> Dict:
        """Execute individual agent subtask"""
        agent = self.agents[agent_name]
        
        messages = [
            {"role": "system", "content": agent.to_system_message()},
            {
                "role": "user",
                "content": f"Task: {task}\n\nShared Workspace Context: {json.dumps(self.shared_state)}"
            }
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=messages
        )
        
        return {
            "agent": agent_name,
            "output": response.choices[0].message.content,
            "usage": response.usage.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _synthesize_results(
        self,
        results: Dict[str, Dict],
        original_task: str
    ) -> str:
        """Synthesize multi-agent results into final output"""
        synthesis_prompt = f"Original Task: {original_task}\n\nAgent Outputs:\n\n"
        
        for agent_name, result in results.items():
            synthesis_prompt += f"### {agent_name}\n{result['output']}\n\n"
        
        synthesis_prompt += "\nSynthesize these outputs into a coherent final result:"
        
        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are a meta-coordinator synthesizing multi-agent outputs into a unified result."
                },
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]
        )
        
        return response.choices[0].message.content
    
    def _log_event(self, event: Dict):
        """Log event to project ledger"""
        event["timestamp"] = datetime.utcnow().isoformat()
        event["workspace_id"] = self.workspace_id
        self.ledger.append(event)
    
    def get_ledger(self, event_type: Optional[str] = None) -> List[Dict]:
        """
        Get project ledger
        Implements Project Ledger from Tech Spec Section 3.7
        """
        if event_type:
            return [e for e in self.ledger if e.get("event_type") == event_type]
        return self.ledger


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_agent_orchestration():
    """Example: Multi-agent orchestration with handoffs"""
    orchestrator = AgentOrchestrator()
    
    # Register personas from Tech Spec
    sora = Agent(
        name="Sora",
        role=AgentRole.SORA,
        instructions="You are a strategic architect. Focus on structure, dependencies, and execution order.",
        tools=["project_planner", "dependency_analyzer"],
        handoff_agents=["Aria", "AIC"]
    )
    
    aria = Agent(
        name="Aria",
        role=AgentRole.ARIA,
        instructions="You are an emotional and symbolic muse. Focus on tone, narrative, and user experience.",
        tools=["content_analyzer", "sentiment_checker"],
        handoff_agents=["Sora"]
    )
    
    orchestrator.register_agent(sora)
    orchestrator.register_agent(aria)
    
    # Execute task
    result = orchestrator.execute_with_agent(
        "Sora",
        "Plan a new feature: AI-powered document summarization with user customization"
    )
    
    print(f"Final agent: {result['final_agent']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Response: {result['response']}")


def example_mcp_integration():
    """Example: MCP driver integration"""
    manager = MCPDriverManager()
    
    # Register GitHub driver
    github_driver = MCPDriver(
        driver_id="github",
        server_url="https://mcp.github.com/v1",
        api_key="ghp_xxxxxxxxxxxxx",
        description="GitHub integration for repository management"
    )
    manager.register_driver(github_driver)
    
    # Execute task using GitHub driver
    result = manager.execute_with_drivers(
        task="List all open issues in the 'main' repository",
        driver_ids=["github"],
        instructions="You are a project manager. Use the GitHub driver to retrieve and summarize issues."
    )
    
    print(f"Response: {result['response']}")
    print(f"Driver calls: {result['total_driver_calls']}")


def example_sandboxed_execution():
    """Example: Sandboxed code execution"""
    executor = SandboxedExecutor("/tmp/sandbox_workspace")
    
    # Execute safe command
    result = executor.execute_command("echo 'Hello, World!'")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    # Apply file patch
    result = executor.apply_patch(
        "hello.py",
        "print('Hello from sandboxed Python!')"
    )
    print(f"File created: {result.success}")


async def example_collaborative_workspace():
    """Example: Multi-agent collaboration"""
    workspace = CollaborativeWorkspace("project-001")
    
    # Register agents
    sora = Agent(
        name="Sora",
        role=AgentRole.SORA,
        instructions="Strategic planner"
    )
    
    aria = Agent(
        name="Aria",
        role=AgentRole.ARIA,
        instructions="UX and content specialist"
    )
    
    workspace.register_agent(sora)
    workspace.register_agent(aria)
    
    # Execute collaborative task
    result = await workspace.execute_collaborative_task(
        "Design a new user onboarding flow",
        required_agents=["Sora", "Aria"],
        execution_mode="parallel"
    )
    
    print(f"Final result: {result['final_result']}")
    print(f"Ledger entries: {result['ledger_entries']}")


def example_rag_with_audit():
    """Example: RAG with audit trail"""
    rag = AuditableRAG()
    
    # Add documents
    docs = [
        Document(
            id="doc1",
            content="The OS Dashboard is a driver-aware AI operating system.",
            metadata={"type": "overview", "version": "6.0"}
        ),
        Document(
            id="doc2",
            content="Capsules are executable workflows with environment specifications.",
            metadata={"type": "concept", "version": "6.0"}
        )
    ]
    rag.add_documents(docs)
    
    # Answer question
    result = rag.answer_question(
        "What are capsules in OS Dashboard?",
        top_k=3
    )
    
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])}")
    
    # Generate evidence pack
    evidence = rag.generate_evidence_pack()
    print(f"Total operations: {evidence['total_operations']}")


if __name__ == "__main__":
    import os
    
    # Set API key
    # os.environ["OPENAI_API_KEY"] = "sk-..."
    
    print("OpenAI Cookbook Integration Samples")
    print("=" * 50)
    print("\nRun individual examples:")
    print("- example_agent_orchestration()")
    print("- example_mcp_integration()")
    print("- example_sandboxed_execution()")
    print("- asyncio.run(example_collaborative_workspace())")
    print("- example_rag_with_audit()")
