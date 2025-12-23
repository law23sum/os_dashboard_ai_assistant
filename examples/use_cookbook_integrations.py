#!/usr/bin/env python3
"""
Example: Using OpenAI Cookbook Integrations in Your Application

This script demonstrates how to use the cookbook integrations
(LlamaIndex, Guidance, Prompttools) in your application code.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def example_llamaindex_rag():
    """Example: Using LlamaIndex for RAG"""
    print("=" * 60)
    print("Example 1: LlamaIndex RAG")
    print("=" * 60)
    
    try:
        from assistant_core.llamaindex_integration import create_rag_engine, query_rag_engine
        
        # Create RAG engine
        print("\n1. Creating RAG engine...")
        engine = create_rag_engine()
        
        if not engine:
            print("   ⚠️  LlamaIndex not available")
            return
        
        print("   ✅ RAG engine created")
        
        # Add documents
        print("\n2. Adding documents...")
        documents = [
            {
                "text": "Python is a high-level programming language.",
                "metadata": {"source": "python_docs"}
            },
            {
                "text": "FastAPI is a modern web framework for building APIs.",
                "metadata": {"source": "fastapi_docs"}
            }
        ]
        
        from assistant_core.llamaindex_integration import add_documents_to_rag
        result = await add_documents_to_rag(engine, documents)
        print(f"   ✅ Added documents: {result.get('status')}")
        
        # Query
        print("\n3. Querying RAG engine...")
        result = await query_rag_engine(engine, "What is Python?")
        print(f"   Response: {result.get('response', 'N/A')[:200]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


def example_guidance_templating():
    """Example: Using Guidance for prompt templating"""
    print("\n" + "=" * 60)
    print("Example 2: Guidance Prompt Templating")
    print("=" * 60)
    
    try:
        from assistant_core.guidance_integration import create_guidance_engine, generate_with_guidance
        
        # Create Guidance engine
        print("\n1. Creating Guidance engine...")
        engine = create_guidance_engine()
        
        if not engine:
            print("   ⚠️  Guidance not available")
            return
        
        print("   ✅ Guidance engine created")
        
        # Generate with template
        print("\n2. Generating text with template...")
        template = """
        {{#system~}}
        You are a helpful assistant.
        {{~/system}}
        
        {{#user~}}
        Write a short greeting for {{name}}.
        {{~/user}}
        
        {{#assistant~}}
        {{gen 'greeting' max_tokens=50}}
        {{~/assistant}}
        """
        
        variables = {"name": "Alice"}
        result = await generate_with_guidance(engine, template, variables)
        print(f"   Generated: {result.get('generated_text', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


def example_api_usage():
    """Example: Using the API endpoints"""
    print("\n" + "=" * 60)
    print("Example 3: Using API Endpoints")
    print("=" * 60)
    
    import requests
    
    api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
    cookbook_base = f"{api_base}/api/cookbook"
    
    print(f"\nAPI Base: {api_base}")
    
    # Check status
    print("\n1. Checking integration status...")
    try:
        response = requests.get(f"{cookbook_base}/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ LlamaIndex: {status.get('llamaindex', False)}")
            print(f"   ✅ Guidance: {status.get('guidance', False)}")
            print(f"   ✅ Prompttools: {status.get('prompttools', False)}")
        else:
            print(f"   ⚠️  Status check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Backend not running. Start with:")
        print("      python -m uvicorn backend_api.main:app --reload")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Query RAG
    print("\n2. Querying RAG via API...")
    try:
        response = requests.post(
            f"{cookbook_base}/rag/query",
            json={"query": "What is Python?", "similarity_top_k": 3},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query successful")
            print(f"   Response: {result.get('response', 'N/A')[:100]}...")
        else:
            print(f"   ⚠️  Query failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")


def example_direct_import():
    """Example: Direct import and usage"""
    print("\n" + "=" * 60)
    print("Example 4: Direct Import Usage")
    print("=" * 60)
    
    print("\nYou can import and use the integrations directly:")
    print("""
    # LlamaIndex RAG
    from assistant_core.llamaindex_integration import (
        create_rag_engine,
        query_rag_engine,
        add_documents_to_rag
    )
    
    engine = create_rag_engine()
    await add_documents_to_rag(engine, documents)
    result = await query_rag_engine(engine, "Your query")
    
    # Guidance
    from assistant_core.guidance_integration import (
        create_guidance_engine,
        generate_with_guidance
    )
    
    engine = create_guidance_engine()
    result = await generate_with_guidance(engine, template, variables)
    
    # Via AI Services API
    from assistant_core.ai_services_api import ai_services_api, AIServiceType, AIServiceRequest
    
    request = AIServiceRequest(
        service_type=AIServiceType.LLAMA_INDEX_RAG,
        input_data={"query": "Your query"}
    )
    response = await ai_services_api.process_request(request)
    """)


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OpenAI Cookbook Integrations - Usage Examples")
    print("=" * 60)
    
    # Run examples
    await example_llamaindex_rag()
    await example_guidance_templating()
    example_api_usage()
    example_direct_import()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - docs/OPENAI_COOKBOOK_INTEGRATIONS.md")
    print("  - docs/QUICK_START_COOKBOOK.md")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

