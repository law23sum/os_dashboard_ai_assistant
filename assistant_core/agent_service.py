"""
Enhanced Agent Service - Incorporating OpenAI Cookbook Best Practices

This service layer provides:
- Tool management and registration
- Agent orchestration
- Role-based routing
- Performance optimization
- Memory management
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import os
from datetime import datetime

from agents_ai import Agent, setup_agents, route_prompt_to_agent, AgentRole, AgentCapability


class ToolType(Enum):
    """Types of tools available to agents"""
    SHELL = "shell"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    CODE_ANALYSIS = "code_analysis"
    WEB_SEARCH = "web_search"
    API_CALL = "api_call"
    DATABASE = "database"
    CUSTOM = "custom"


@dataclass
class ToolDefinition:
    """Definition of a tool for agent use"""
    name: str
    tool_type: ToolType
    description: str
    handler: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class AgentToolManager:
    """
    Manages tools for agents - inspired by OpenAI cookbook patterns
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools available to all agents"""
        from agents_ai import ToolRegistry
        
        # Shell execution
        self.register_tool(ToolDefinition(
            name="run_shell",
            tool_type=ToolType.SHELL,
            description="Execute a shell command in the Unix environment",
            handler=ToolRegistry.run_shell,
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    }
                },
                "required": ["command"]
            }
        ))
        
        # File operations
        self.register_tool(ToolDefinition(
            name="read_file",
            tool_type=ToolType.FILE_READ,
            description="Read the contents of a file",
            handler=ToolRegistry.read_file,
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ))
        
        self.register_tool(ToolDefinition(
            name="write_file",
            tool_type=ToolType.FILE_WRITE,
            description="Write content to a file (overwrites existing)",
            handler=ToolRegistry.write_file,
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ))
    
    def register_tool(self, tool: ToolDefinition):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool_definitions(self, agent_role: Optional[AgentRole] = None) -> List[Dict[str, Any]]:
        """Get tool definitions for an agent, filtered by role if specified"""
        definitions = []
        for name, tool in self.tools.items():
            if tool.enabled:
                # Role-based tool filtering can be added here
                definitions.append(tool.to_openai_format())
        return definitions
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with given arguments"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        if not tool.enabled:
            raise ValueError(f"Tool '{tool_name}' is disabled")
        
        # Execute the tool handler
        if tool.tool_type == ToolType.SHELL:
            return tool.handler(arguments.get("command", ""))
        elif tool.tool_type in [ToolType.FILE_READ, ToolType.FILE_WRITE]:
            if tool.tool_type == ToolType.FILE_READ:
                return tool.handler(arguments.get("path", ""))
            else:
                return tool.handler(
                    arguments.get("path", ""),
                    arguments.get("content", "")
                )
        else:
            return tool.handler(**arguments)


class AgentOrchestrator:
    """
    Orchestrates multiple agents with role-based routing and priority
    Incorporates best practices from OpenAI cookbook multi-agent patterns
    """
    
    def __init__(self):
        self.agents = setup_agents()
        self.tool_manager = AgentToolManager()
        self.conversation_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
    
    def route_and_execute(
        self,
        prompt: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a prompt to appropriate agent(s) and execute
        
        Returns:
            Dict with agent responses, routing decision, and metadata
        """
        # Route prompt to appropriate agents
        routed_agents = route_prompt_to_agent(prompt, self.agents)
        
        responses = {}
        start_time = datetime.now()
        
        # Get responses from routed agents in priority order
        for agent_name in routed_agents:
            agent = self.agents[agent_name]
            
            # Add context if provided
            full_prompt = prompt
            if user_context:
                context_str = json.dumps(user_context, indent=2)
                full_prompt = f"{prompt}\n\nContext:\n{context_str}"
            
            try:
                response = agent.chat(full_prompt)
                responses[agent_name] = {
                    "response": response,
                    "agent": agent_name,
                    "role": agent.role_desc[:100] + "..." if len(agent.role_desc) > 100 else agent.role_desc,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                responses[agent_name] = {
                    "error": str(e),
                    "agent": agent_name,
                    "timestamp": datetime.now().isoformat()
                }
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Update performance metrics
        self._update_metrics(routed_agents, execution_time)
        
        return {
            "prompt": prompt,
            "routed_agents": routed_agents,
            "responses": responses,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_metrics(self, agents: List[str], execution_time: float):
        """Update performance metrics"""
        for agent_name in agents:
            if agent_name not in self.performance_metrics:
                self.performance_metrics[agent_name] = {
                    "call_count": 0,
                    "total_time": 0.0,
                    "average_time": 0.0
                }
            
            metrics = self.performance_metrics[agent_name]
            metrics["call_count"] += 1
            metrics["total_time"] += execution_time
            metrics["average_time"] = metrics["total_time"] / metrics["call_count"]
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        return self.performance_metrics
    
    def collaborate(
        self,
        task: str,
        agent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Have multiple agents collaborate on a task
        """
        if agent_names is None:
            agent_names = list(self.agents.keys())
        
        # Each agent provides their perspective
        individual_analyses = {}
        for agent_name in agent_names:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                analysis = agent.chat(
                    f"Analyze this task from your specialized perspective: {task}\n\n"
                    f"Consider your role: {agent.role_desc[:200]}...\n\n"
                    f"Provide a detailed analysis and recommendations."
                )
                individual_analyses[agent_name] = analysis
        
        # Agents can then discuss with each other
        # (This can be enhanced with inter-agent messaging)
        
        return {
            "task": task,
            "participants": agent_names,
            "individual_analyses": individual_analyses,
            "timestamp": datetime.now().isoformat()
        }


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create the global agent orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator

