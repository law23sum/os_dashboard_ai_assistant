#!/usr/bin/env python3
"""
Test script for RAG + Prompt Tooling API endpoints

This script tests the RAG and prompt tooling endpoints to ensure
they are working correctly.
"""

import requests
import json
import sys
import os
from typing import Dict, Any

# Default API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TOOLING_BASE = f"{API_BASE_URL}/api/ai-tooling"


def test_status_endpoint() -> Dict[str, Any]:
    """Test the status endpoint"""
    print("=" * 60)
    print("Testing Status Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{TOOLING_BASE}/status", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status endpoint working")
        print(f"   LlamaIndex: {data.get('llamaindex', False)}")
        print(f"   Guidance: {data.get('guidance', False)}")
        print(f"   Prompttools: {data.get('prompttools', False)}")
        print(f"   OpenAI API Key Set: {data.get('openai_api_key_set', False)}")
        
        return {"success": True, "data": data}
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_BASE_URL}")
        print("   Make sure the backend server is running:")
        print("   python -m uvicorn backend_api.main:app --reload")
        return {"success": False, "error": "Connection refused"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def test_rag_query_endpoint() -> Dict[str, Any]:
    """Test the RAG query endpoint"""
    print("\n" + "=" * 60)
    print("Testing RAG Query Endpoint")
    print("=" * 60)
    
    # First, add some test documents
    print("\n1. Adding test documents...")
    try:
        add_docs_response = requests.post(
            f"{TOOLING_BASE}/rag/documents",
            json={
                "documents": [
                    "Python is a high-level programming language known for its simplicity.",
                    "FastAPI is a modern web framework for building APIs with Python.",
                    "LlamaIndex is a framework for building LLM applications with RAG capabilities.",
                ],
                "metadata": {"source": "test"}
            },
            timeout=30
        )
        if add_docs_response.status_code == 200:
            print("   ✅ Documents added successfully")
        else:
            print(f"   ⚠️  Could not add documents: {add_docs_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Could not add documents: {e}")
    
    # Now test query
    print("\n2. Testing RAG query...")
    try:
        response = requests.post(
            f"{TOOLING_BASE}/rag/query",
            json={
                "query": "What is Python?",
                "similarity_top_k": 3,
                "response_mode": "compact"
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ RAG query successful")
        print(f"   Response: {data.get('response', 'N/A')[:100]}...")
        print(f"   Source nodes: {len(data.get('source_nodes', []))}")
        
        return {"success": True, "data": data}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            print("   ⚠️  RAG service not available (LlamaIndex may not be initialized)")
        else:
            print(f"   ❌ HTTP Error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def test_guidance_endpoint() -> Dict[str, Any]:
    """Test the Guidance template endpoint"""
    print("\n" + "=" * 60)
    print("Testing Guidance Template Endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{TOOLING_BASE}/guidance/template",
            json={
                "template": "Hello {{name}}, welcome to {{platform}}!",
                "variables": {
                    "name": "Developer",
                    "platform": "OpenAI reference guides"
                }
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Guidance template successful")
        print(f"   Generated text: {data.get('generated_text', 'N/A')}")
        
        return {"success": True, "data": data}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            print("   ⚠️  Guidance service not available")
        else:
            print(f"   ❌ HTTP Error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def test_rag_context_endpoint() -> Dict[str, Any]:
    """Test the RAG context endpoint"""
    print("\n" + "=" * 60)
    print("Testing RAG Context Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{TOOLING_BASE}/rag/context",
            params={"query": "Python programming", "top_k": 3},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ RAG context retrieval successful")
        print(f"   Context chunks: {len(data.get('chunks', []))}")
        
        return {"success": True, "data": data}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            print("   ⚠️  RAG service not available")
        else:
            print(f"   ❌ HTTP Error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RAG + Prompt Tooling API Test")
    print("=" * 60)
    print(f"\nTesting API at: {API_BASE_URL}")
    print(f"Tooling endpoints: {TOOLING_BASE}")
    print()
    
    results = {
        "status": test_status_endpoint(),
        "rag_query": test_rag_query_endpoint(),
        "guidance": test_guidance_endpoint(),
        "rag_context": test_rag_context_endpoint(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r.get("success", False))
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {name}")
    
    print(f"\nSuccessful: {successful}/{total}")
    
    if successful == total:
        print("✅ All tests passed!")
        return 0
    elif successful > 0:
        print("⚠️  Some tests passed. Check errors above.")
        return 1
    else:
        print("❌ All tests failed. Check if backend is running.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
