#!/usr/bin/env python3
"""
Verification Script for RAG + Prompt Tooling Integrations

This script checks if all integrated tools are properly installed
and can be imported successfully.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def check_integration(integration_name, module_path):
    """Check if an integration module can be imported"""
    try:
        module = __import__(module_path, fromlist=[integration_name])
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    """Run verification checks"""
    print("=" * 60)
    print("RAG + Prompt Tooling Integrations - Verification")
    print("=" * 60)
    print()

    results = {
        "LlamaIndex": False,
        "Guidance": False,
        "Prompttools": False,
    }

    # Check LlamaIndex
    print("Checking LlamaIndex...")
    llama_available, llama_error = check_import("llama_index")
    if llama_available:
        integration_ok, integration_error = check_integration(
            "LlamaIndexRAGEngine",
            "assistant_core.llamaindex_integration"
        )
        if integration_ok:
            print("  ✅ LlamaIndex installed and integration available")
            results["LlamaIndex"] = True
        else:
            print(f"  ⚠️  LlamaIndex installed but integration failed: {integration_error}")
    else:
        print(f"  ❌ LlamaIndex not installed: {llama_error}")
        print("     Install with: pip install llama-index llama-index-embeddings-openai llama-index-llms-openai")
    print()

    # Check Guidance
    print("Checking Guidance...")
    guidance_available, guidance_error = check_import("guidance")
    if guidance_available:
        integration_ok, integration_error = check_integration(
            "GuidancePromptEngine",
            "assistant_core.guidance_integration"
        )
        if integration_ok:
            print("  ✅ Guidance installed and integration available")
            results["Guidance"] = True
        else:
            print(f"  ⚠️  Guidance installed but integration failed: {integration_error}")
    else:
        print(f"  ❌ Guidance not installed: {guidance_error}")
        print("     Install with: pip install guidance")
    print()

    # Check Prompttools
    print("Checking Prompttools...")
    prompttools_available = False
    prompttools_error = None
    try:
        import prompttools
        prompttools_available = True
    except (ImportError, AttributeError, Exception) as e:
        prompttools_error = str(e)
        if "openai" in str(e).lower() and "error" in str(e).lower():
            prompttools_error = "Compatibility issue with OpenAI 2.x (prompttools expects OpenAI 1.x)"
    if prompttools_available:
        integration_ok, integration_error = check_integration(
            "PromptEvaluator",
            "assistant_core.prompttools_integration"
        )
        if integration_ok:
            print("  ✅ Prompttools installed and integration available")
            results["Prompttools"] = True
        else:
            print(f"  ⚠️  Prompttools installed but integration failed: {integration_error}")
    else:
        print(f"  ❌ Prompttools not installed: {prompttools_error}")
        print("     Install with: pip install prompttools")
    print()

    # Check OpenAI API Key
    print("Checking OpenAI API Key...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
        print(f"  ✅ OPENAI_API_KEY is set: {masked_key}")
    else:
        print("  ⚠️  OPENAI_API_KEY not set")
        print("     Set it with: export OPENAI_API_KEY=sk-...")
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    total = len(results)
    installed = sum(1 for v in results.values() if v)
    
    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {name}: {'Available' if status else 'Not installed'}")
    
    print()
    print(f"Installed: {installed}/{total}")
    
    if installed == total:
        print("✅ All integrations are available!")
    elif installed > 0:
        print("⚠️  Some integrations are missing. Install missing packages.")
    else:
        print("❌ No integrations installed. Run: pip install -r requirements.txt")
    
    print()
    print("For examples, run: python examples/use_rag_prompt_tooling.py")
    print("=" * 60)

    # Exit code
    return 0 if installed == total else 1

if __name__ == "__main__":
    sys.exit(main())

