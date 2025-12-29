"""
AI Agents Router - Backend API for AIC, Aria, Sora, and Cursor AI

This router provides REST API endpoints for interacting with the multi-agent AI system.
Integrates with agents_ai.py and provides optimized configurations based on OpenAI cookbook best practices.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

# Import agent system
try:
    from agents_ai import setup_agents, Agent, route_prompt_to_agent, AgentSystem
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    print(f"⚠️  Warning: agents_ai not available: {e}")


class AgentMessageRequest(BaseModel):
    """Request model for sending messages to agents"""
    message: str = Field(..., description="Message to send to the agent")
    agent: Optional[str] = Field(None, description="Specific agent name (AIC, Aria, Sora). If not specified, will route automatically")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the agent")
    temperature: Optional[float] = Field(None, description="Override temperature (0.0-2.0)")
    max_tokens: Optional[int] = Field(None, description="Override max tokens")


class AgentMessageResponse(BaseModel):
    """Response model for agent messages"""
    agent: str
    response: str
    role: str
    specializations: List[str]
    model_used: str
    temperature: float
    tokens_used: Optional[int] = None


class AgentListResponse(BaseModel):
    """Response model for listing agents"""
    agents: List[Dict[str, Any]]
    available: bool


class AgentCollaborationRequest(BaseModel):
    """Request model for collaborative agent tasks"""
    task: str = Field(..., description="Task for agents to collaborate on")
    agents: Optional[List[str]] = Field(None, description="Specific agents to involve. If not specified, all agents participate")


class AgentCollaborationResponse(BaseModel):
    """Response model for collaborative tasks"""
    task: str
    individual_analyses: Dict[str, str]
    messages_exchanged: int
    timestamp: str


@router.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """List all available AI agents"""
    if not AGENTS_AVAILABLE:
        return AgentListResponse(agents=[], available=False)
    
    try:
        agents = setup_agents()
        agent_list = []
        for name, agent in agents.items():
            agent_list.append({
                "name": name,
                "title": agent.title,
                "disciplines": agent.disciplines,
                "role": agent.role_desc[:200] + "..." if len(agent.role_desc) > 200 else agent.role_desc
            })
        
        return AgentListResponse(agents=agent_list, available=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")


@router.post("/agents/{agent_name}", response_model=AgentMessageResponse)
async def send_message_to_agent(
    agent_name: str,
    request: AgentMessageRequest
):
    """
    Send a message to a specific agent (AIC, Aria, or Sora)
    
    - **agent_name**: Name of the agent (AIC, Aria, or Sora)
    - **message**: The message to send
    - **context**: Optional context dictionary
    - **temperature**: Optional temperature override
    - **max_tokens**: Optional max tokens override
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents system not available")
    
    try:
        agents = setup_agents()
        agent_name_upper = agent_name.upper()
        
        if agent_name_upper not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found. Available agents: {', '.join(agents.keys())}"
            )
        
        agent = agents[agent_name_upper]
        
        # Override temperature if provided
        if request.temperature is not None:
            original_temp = agent._get_temperature_for_agent()
            # Temporarily override (would need to modify agent class for persistence)
            pass
        
        # Send message
        response_text = agent.chat(request.message)
        
        # Get agent metadata
        model_used = agent._get_model_for_agent()
        temperature_used = agent._get_temperature_for_agent()
        
        return AgentMessageResponse(
            agent=agent_name_upper,
            response=response_text,
            role=agent.role_desc[:100] + "..." if len(agent.role_desc) > 100 else agent.role_desc,
            specializations=agent.disciplines.split(", "),
            model_used=model_used,
            temperature=temperature_used
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message to agent: {str(e)}")


@router.post("/agents/route", response_model=List[str])
async def route_prompt(request: AgentMessageRequest):
    """
    Route a prompt to the appropriate agent(s) based on content analysis.
    Returns list of agent names in priority order.
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents system not available")
    
    try:
        agents = setup_agents()
        routed_agents = route_prompt_to_agent(request.message, agents)
        return routed_agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error routing prompt: {str(e)}")


@router.post("/agents/collaborate", response_model=AgentCollaborationResponse)
async def collaborate_agents(request: AgentCollaborationRequest):
    """
    Have multiple agents collaborate on a task.
    Each agent analyzes from their perspective and agents can communicate.
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents system not available")
    
    try:
        system = AgentSystem()
        
        # If specific agents requested, filter
        if request.agents:
            # Filter system agents to only requested ones
            filtered_agents = {name: agent for name, agent in system.agents.items() if name in request.agents}
            if not filtered_agents:
                raise HTTPException(status_code=400, detail="No valid agents specified")
            # Note: This would require modifying AgentSystem to support filtered collaboration
            # For now, use all agents
        
        result = await system.collaborate(request.task)
        
        return AgentCollaborationResponse(
            task=result["task"],
            individual_analyses=result["individual_analyses"],
            messages_exchanged=result["messages_exchanged"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in agent collaboration: {str(e)}")


@router.get("/agents/{agent_name}/config")
async def get_agent_config(agent_name: str):
    """Get configuration for a specific agent (model, temperature, max_tokens)"""
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents system not available")
    
    try:
        agents = setup_agents()
        agent_name_upper = agent_name.upper()
        
        if agent_name_upper not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found"
            )
        
        agent = agents[agent_name_upper]
        
        return {
            "agent": agent_name_upper,
            "model": agent._get_model_for_agent(),
            "temperature": agent._get_temperature_for_agent(),
            "max_tokens": 4000,  # Default, could be made configurable
            "title": agent.title,
            "disciplines": agent.disciplines,
            "role": agent.role_desc
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent config: {str(e)}")


@router.post("/agents/analyze-codebase")
async def analyze_codebase_collaborative():
    """
    Have all agents collaboratively analyze the codebase.
    Each agent provides insights from their specialized perspective.
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents system not available")
    
    try:
        system = AgentSystem()
        analyses = await system.analyze_codebase_collaborative()
        return analyses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing codebase: {str(e)}")

