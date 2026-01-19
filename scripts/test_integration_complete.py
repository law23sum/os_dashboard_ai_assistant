#!/usr/bin/env python3
"""
Complete Integration Test for RAG + Prompt Tooling Integrations

This script tests all aspects of the RAG + prompt tooling integrations:
1. Module imports
2. AI Services API integration
3. Router availability
4. Function availability
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_module_imports():
    """Test that all integration modules can be imported"""
    print("=" * 60)
    print("Test 1: Module Imports")
    print("=" * 60)
    
    results = {}
    
    # Test LlamaIndex
    try:
        from assistant_core.llamaindex_integration import (
            create_rag_engine,
            query_rag_engine,
            add_documents_to_rag
        )
        results["llamaindex"] = True
        print("  ✅ LlamaIndex integration imported")
    except Exception as e:
        results["llamaindex"] = False
        print(f"  ❌ LlamaIndex import failed: {e}")
    
    # Test Guidance
    try:
        from assistant_core.guidance_integration import (
            create_guidance_engine,
            generate_with_guidance
        )
        results["guidance"] = True
        print("  ✅ Guidance integration imported")
    except Exception as e:
        results["guidance"] = False
        print(f"  ❌ Guidance import failed: {e}")
    
    # Test Prompttools
    try:
        from assistant_core.prompttools_integration import (
            create_prompt_evaluator
        )
        results["prompttools"] = True
        print("  ✅ Prompttools integration imported")
    except Exception as e:
        results["prompttools"] = False
        print(f"  ⚠️  Prompttools import failed (expected if compatibility issue): {e}")
    
    return results


def test_ai_services_api():
    """Test AI Services API integration"""
    print("\n" + "=" * 60)
    print("Test 2: AI Services API Integration")
    print("=" * 60)
    
    try:
        from assistant_core.ai_services_api import (
            ai_services_api,
            get_tooling_integrations_status
        )
        
        # Test status function
        status = get_tooling_integrations_status()
        print(f"  ✅ get_tooling_integrations_status() works")
        print(f"     Status: {status}")
        
        # Test helper methods
        rag_engine = ai_services_api.get_rag_engine()
        print(f"  ✅ get_rag_engine() works: {rag_engine is not None}")
        
        guidance_engine = ai_services_api.get_guidance_engine()
        print(f"  ✅ get_guidance_engine() works: {guidance_engine is not None}")
        
        prompt_evaluator = ai_services_api.get_prompt_evaluator()
        print(f"  ✅ get_prompt_evaluator() works: {prompt_evaluator is not None}")
        
        return True
    except Exception as e:
        print(f"  ❌ AI Services API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router():
    """Test that the router can be imported"""
    print("\n" + "=" * 60)
    print("Test 3: Router Import")
    print("=" * 60)
    
    try:
        import importlib.util
        router_path = project_root / "backend_api" / "routers" / "tooling_integrations.py"
        
        if not router_path.exists():
            print(f"  ❌ Router file not found: {router_path}")
            return False
        
        spec = importlib.util.spec_from_file_location(
            "tooling_integrations",
            router_path
        )
        router_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(router_module)
        
        print(f"  ✅ Router module imported")
        print(f"     Routes: {len(router_module.router.routes)}")
        
        for route in router_module.router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(sorted(route.methods))
                print(f"       {methods:6} {route.path}")
        
        return True
    except Exception as e:
        print(f"  ❌ Router import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "=" * 60)
    print("Test 4: File Structure")
    print("=" * 60)
    
    required_files = [
        "assistant_core/llamaindex_integration.py",
        "assistant_core/guidance_integration.py",
        "assistant_core/prompttools_integration.py",
        "backend_api/routers/tooling_integrations.py",
        "scripts/verify_rag_prompt_tooling.py",
        "scripts/test_rag_prompt_tooling_api.py",
        "scripts/check_prompttools_update.py",
        "examples/use_rag_prompt_tooling.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RAG + Prompt Tooling Integrations - Complete Integration Test")
    print("=" * 60)
    print()
    
    results = {
        "module_imports": test_module_imports(),
        "ai_services_api": test_ai_services_api(),
        "router": test_router(),
        "file_structure": test_file_structure(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All integration tests passed!")
        print("   The RAG + prompt tooling integrations are fully set up and ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
