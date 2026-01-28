"""
OpenAI Cookbook Integrations Router

This router exposes the OpenAI Cookbook integrations (LlamaIndex, Guidance, Prompttools)
through REST API endpoints.

All integrations are MIT licensed and safe for commercial use.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

# Import integrations
try:
    from assistant_core.ai_services_api import (
        get_cookbook_integrations_status,
        ai_services_api,
    )
    from assistant_core.llamaindex_integration import create_rag_engine
    from assistant_core.guidance_integration import create_guidance_engine
    from assistant_core.prompttools_integration import create_prompt_evaluator
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    print(f"⚠️  Warning: Cookbook integrations not fully available: {e}")


# Request/Response Models
class IntegrationStatusResponse(BaseModel):
    """Status of cookbook integrations"""
    llamaindex: bool
    guidance: bool
    prompttools: bool
    openai_api_key_set: bool


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""
    query: str = Field(..., description="Query text")
    similarity_top_k: int = Field(5, ge=1, le=20, description="Number of top results")
    response_mode: str = Field("compact", description="Response mode")


class RAGAddDocumentsRequest(BaseModel):
    """Request to add documents to RAG index"""
    documents: List[str] = Field(..., description="List of document texts")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class GuidanceTemplateRequest(BaseModel):
    """Request for Guidance template generation"""
    template: str = Field(..., description="Guidance template (Handlebars syntax)")
    variables: Dict[str, Any] = Field(..., description="Variables to inject into template")


class PromptEvaluationRequest(BaseModel):
    """Request for prompt evaluation"""
    prompts: List[str] = Field(..., description="List of prompts to evaluate")
    test_inputs: Optional[List[str]] = Field(None, description="Test inputs")
    model: str = Field("gpt-4o-mini", description="Model to use")


@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integrations_status():
    """
    Get the status of all OpenAI Cookbook integrations.
    
    Returns which integrations are available and if OpenAI API key is set.
    """
    try:
        status = get_cookbook_integrations_status()
        
        # Check environment variable
        import os
        api_key_set = bool(os.getenv("OPENAI_API_KEY"))
        
        return IntegrationStatusResponse(
            llamaindex=status.get("llamaindex", False),
            guidance=status.get("guidance", False),
            prompttools=status.get("prompttools", False),
            openai_api_key_set=api_key_set,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/rag/query")
async def rag_query(request: RAGQueryRequest):
    """
    Query the LlamaIndex RAG engine.
    
    Requires LlamaIndex to be installed and OpenAI API key to be set.
    """
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Cookbook integrations not available. Install dependencies: pip install llama-index"
        )
    
    try:
        rag_engine = ai_services_api.get_rag_engine()
        if not rag_engine:
            raise HTTPException(
                status_code=503,
                detail="LlamaIndex RAG engine not available. Install with: pip install llama-index"
            )
        
        result = rag_engine.query(
            query_text=request.query,
            similarity_top_k=request.similarity_top_k,
            response_mode=request.response_mode,
        )
        
        return {
            "success": True,
            "response": result.get("response"),
            "source_nodes": result.get("source_nodes", []),
            "query": result.get("query"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/rag/documents")
async def rag_add_documents(request: RAGAddDocumentsRequest):
    """
    Add documents to the LlamaIndex RAG engine.
    
    Requires LlamaIndex to be installed and OpenAI API key to be set.
    """
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Cookbook integrations not available. Install dependencies: pip install llama-index"
        )
    
    try:
        rag_engine = ai_services_api.get_rag_engine()
        if not rag_engine:
            raise HTTPException(
                status_code=503,
                detail="LlamaIndex RAG engine not available. Install with: pip install llama-index"
            )
        
        rag_engine.add_documents(
            documents=request.documents,
            metadata=request.metadata,
        )
        
        return {
            "success": True,
            "message": f"Added {len(request.documents)} documents to RAG index",
            "documents_count": len(request.documents),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add documents: {str(e)}")


@router.post("/guidance/template")
async def guidance_template(request: GuidanceTemplateRequest):
    """
    Generate text using a Guidance template.
    
    Requires Guidance to be installed and OpenAI API key to be set.
    """
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Cookbook integrations not available. Install dependencies: pip install guidance"
        )
    
    try:
        guidance_engine = ai_services_api.get_guidance_engine()
        if not guidance_engine:
            raise HTTPException(
                status_code=503,
                detail="Guidance engine not available. Install with: pip install guidance"
            )
        
        result = guidance_engine.generate_with_template(
            template=request.template,
            variables=request.variables,
        )
        
        return {
            "success": True,
            "output": result.get("output"),
            "variables": result.get("variables"),
            "metadata": result.get("metadata"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Guidance generation failed: {str(e)}")


@router.get("/rag/context")
async def rag_get_context(
    query: str = Query(..., description="Query text"),
    max_chunks: int = Query(5, ge=1, le=20, description="Maximum number of context chunks")
):
    """
    Get relevant context chunks for a query without generating a response.
    
    Useful for augmenting prompts with context.
    """
    if not INTEGRATIONS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Cookbook integrations not available. Install dependencies: pip install llama-index"
        )
    
    try:
        rag_engine = ai_services_api.get_rag_engine()
        if not rag_engine:
            raise HTTPException(
                status_code=503,
                detail="LlamaIndex RAG engine not available. Install with: pip install llama-index"
            )
        
        context = rag_engine.get_context_for_query(
            query_text=query,
            max_chunks=max_chunks,
        )
        
        return {
            "success": True,
            "query": query,
            "context_chunks": context,
            "count": len(context),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get context: {str(e)}")

