#!/usr/bin/env python3
"""
Interactive terminal chat with multiple AI providers.

This script allows you to select and chat with different AI providers:
- OpenAI (GPT models)
- Anthropic (Claude)
- Google (Gemini)
- xAI (Grok)
- Cursor IDE

Usage:
    cursor_ai
    cursor_ai --provider openai
    cursor_ai --help
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

try:
    import readline  # For better input handling on Unix
except ImportError:
    readline = None

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
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
        # Remove quotes if present
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)

# Load .env file from project root FIRST, before providers are initialized
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Also try loading from config module if it exists
try:
    from config.config import load_dotenv as config_load_dotenv
    config_load_dotenv()
except ImportError:
    pass


class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self, name: str, api_key_env: str):
        self.name = name
        self.api_key_env = api_key_env
        self.api_key = os.getenv(api_key_env)
        self.client = None
    
    def is_available(self) -> bool:
        """Check if provider is available (API key set)."""
        return self.api_key is not None
    
    def initialize(self):
        """Initialize the provider client."""
        raise NotImplementedError
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Send chat messages and get response."""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI provider (GPT models)."""
    
    def __init__(self):
        super().__init__("OpenAI", "OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    def initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ OpenAI client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class AnthropicProvider(AIProvider):
    """Anthropic provider (Claude)."""
    
    def __init__(self):
        super().__init__("Anthropic (Claude)", "ANTHROPIC_API_KEY")
        self.default_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    def initialize(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            return True
        except ImportError:
            print("⚠️  anthropic package not installed. Install with: pip install anthropic")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Anthropic client not initialized"
        
        try:
            # Anthropic uses a different message format
            system_msg = None
            chat_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    # Convert to Anthropic format
                    role = "user" if msg["role"] == "user" else "assistant"
                    chat_messages.append({"role": role, "content": msg["content"]})
            
            response = self.client.messages.create(
                model=model or self.default_model,
                max_tokens=4096,
                system=system_msg if system_msg else "You are a helpful assistant.",
                messages=chat_messages,
            )
            
            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return "No response"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class GoogleProvider(AIProvider):
    """Google provider (Gemini)."""
    
    def __init__(self):
        super().__init__("Google (Gemini)", "GOOGLE_API_KEY")
        self.default_model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    
    def initialize(self):
        try:
            import google.genai as genai
            self.client = genai.Client(api_key=self.api_key)
            return True
        except ImportError:
            print("⚠️  google-genai package not installed. Install with: pip install google-genai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Google client not initialized"
        
        try:
            # Build conversation context
            # Gemini uses a different format, so we'll build context from recent messages
            context_parts = []
            for msg in messages[-10:]:  # Last 10 messages for context
                if msg["role"] == "system":
                    continue  # Skip system messages for now
                elif msg["role"] == "user":
                    context_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    context_parts.append(f"Assistant: {msg['content']}")
            
            # Use the full context as prompt
            full_prompt = "\n".join(context_parts)
            if not full_prompt.strip():
                full_prompt = messages[-1]["content"] if messages else ""
            
            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"


class GrokProvider(AIProvider):
    """xAI provider (Grok)."""
    
    def __init__(self):
        super().__init__("xAI (Grok)", "XAI_API_KEY")
        self.default_model = os.getenv("XAI_MODEL", "grok-beta")
        self.base_url = "https://api.x.ai/v1"
    
    def initialize(self):
        # Grok uses OpenAI-compatible API
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Grok client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class MistralProvider(AIProvider):
    """Mistral AI provider."""
    
    def __init__(self):
        super().__init__("Mistral AI", "MISTRAL_API_KEY")
        self.default_model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        self.base_url = "https://api.mistral.ai/v1"
    
    def initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Mistral client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class CohereProvider(AIProvider):
    """Cohere AI provider."""
    
    def __init__(self):
        super().__init__("Cohere", "COHERE_API_KEY")
        self.default_model = os.getenv("COHERE_MODEL", "command-r-plus")
    
    def initialize(self):
        try:
            import cohere
            self.client = cohere.Client(api_key=self.api_key)
            return True
        except ImportError:
            print("⚠️  cohere package not installed. Install with: pip install cohere")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Cohere client not initialized"
        
        try:
            # Convert messages to Cohere format
            chat_history = []
            prompt = messages[-1]["content"] if messages else ""
            
            for i in range(len(messages) - 1):
                msg = messages[i]
                if msg["role"] == "user":
                    chat_history.append({"role": "USER", "message": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})
            
            response = self.client.chat(
                model=model or self.default_model,
                message=prompt,
                chat_history=chat_history if chat_history else None,
            )
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"


class PerplexityProvider(AIProvider):
    """Perplexity AI provider."""
    
    def __init__(self):
        super().__init__("Perplexity", "PERPLEXITY_API_KEY")
        self.default_model = os.getenv("PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online")
        self.base_url = "https://api.perplexity.ai"
    
    def initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Perplexity client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class TogetherProvider(AIProvider):
    """Together AI provider."""
    
    def __init__(self):
        super().__init__("Together AI", "TOGETHER_API_KEY")
        self.default_model = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")
        self.base_url = "https://api.together.xyz/v1"
    
    def initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ Together AI client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider."""
    
    def __init__(self):
        super().__init__("DeepSeek", "DEEPSEEK_API_KEY")
        self.default_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = "https://api.deepseek.com"
    
    def initialize(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            return True
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.client:
            return "❌ DeepSeek client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


def _find_cursor_api_key() -> Optional[str]:
    """Try to find Cursor API key from various sources."""
    import base64
    
    # First, check environment variable
    key = os.getenv("CURSOR_API_KEY")
    if key:
        return key
    
    # Try to find in Cursor's config files
    cursor_config_paths = [
        Path.home() / "Library/Application Support/Cursor/User/settings.json",
        Path.home() / ".cursor/settings.json",
        Path.home() / ".config/cursor/settings.json",
    ]
    
    for config_path in cursor_config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Look for API key in various possible locations
                    for key_path in [
                        "cursor.apiKey",
                        "cursor.api_key",
                        "cursorApiKey",
                        "apiKey",
                        "api_key",
                        "cursor.token",
                        "cursor.token",
                    ]:
                        keys = key_path.split(".")
                        value = config
                        for k in keys:
                            if isinstance(value, dict) and k in value:
                                value = value[k]
                                if isinstance(value, str) and value:
                                    return value
                            else:
                                break
            except (json.JSONDecodeError, IOError):
                continue
    
    # Try to find in .env file
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("CURSOR_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except IOError:
            pass
    
    return None


class CursorProvider(AIProvider):
    """Cursor IDE provider (uses Cursor's underlying AI providers)."""
    
    def __init__(self):
        # Try to auto-detect API keys from Cursor's config
        _auto_detect_cursor_keys()
        
        super().__init__("Cursor", "CURSOR_API_KEY")
        self.default_model = os.getenv("CURSOR_MODEL", "claude-3-5-sonnet-20241022")
        self.base_url = "https://api.cursor.com"
        self.fallback_provider = None
    
    def is_available(self) -> bool:
        """Check if provider is available (has underlying AI provider keys)."""
        # Cursor uses OpenAI or Anthropic internally, so check for those
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        return bool(openai_key or anthropic_key)
    
    def initialize(self):
        """Initialize the Cursor provider using underlying AI providers."""
        # Try to auto-detect keys one more time
        _auto_detect_cursor_keys()
        
        # Cursor uses OpenAI or Anthropic models internally
        # Prefer Anthropic (Claude) as that's Cursor's default, then OpenAI
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if anthropic_key:
            try:
                import anthropic
                self.fallback_provider = AnthropicProvider()
                self.fallback_provider.api_key = anthropic_key
                if self.fallback_provider.initialize():
                    self.default_model = os.getenv("CURSOR_MODEL", "claude-3-5-sonnet-20241022")
                    return True
            except ImportError:
                pass
        
        if openai_key:
            try:
                from openai import OpenAI
                self.fallback_provider = OpenAIProvider()
                self.fallback_provider.api_key = openai_key
                if self.fallback_provider.initialize():
                    self.default_model = os.getenv("CURSOR_MODEL", "gpt-4")
                    return True
            except ImportError:
                pass
        
        print("⚠️  Cursor provider requires OpenAI or Anthropic API keys.")
        print("   Cursor uses these providers internally for AI features.")
        print("   Please set one of:")
        print("   - OPENAI_API_KEY (for GPT models)")
        print("   - ANTHROPIC_API_KEY (for Claude models)")
        print("   Or add to your .env file")
        return False
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Send chat messages using Cursor's underlying AI provider."""
        if not self.fallback_provider:
            return "❌ Cursor provider not initialized. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY."
        
        try:
            return self.fallback_provider.chat(messages, model or self.default_model)
        except Exception as e:
            return f"❌ Error: {str(e)}"


def _auto_detect_cursor_keys() -> None:
    """Try to automatically detect and set API keys from Cursor's configuration."""
    cursor_config_paths = [
        Path.home() / "Library/Application Support/Cursor/User/settings.json",
        Path.home() / ".cursor/settings.json",
        Path.home() / ".config/cursor/settings.json",
    ]
    
    for config_path in cursor_config_paths:
        if not config_path.exists():
            continue
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
                # Look for OpenAI API key
                if not os.getenv("OPENAI_API_KEY"):
                    for key_path in [
                        "openai.apiKey",
                        "openai.api_key",
                        "openaiApiKey",
                        "cursor.openai.key",
                        "cursor.openai.apiKey",
                    ]:
                        value = _get_nested_value(config, key_path)
                        if value and isinstance(value, str):
                            os.environ["OPENAI_API_KEY"] = value
                            break
                
                # Look for Anthropic API key
                if not os.getenv("ANTHROPIC_API_KEY"):
                    for key_path in [
                        "anthropic.apiKey",
                        "anthropic.api_key",
                        "anthropicApiKey",
                        "cursor.anthropic.key",
                        "cursor.anthropic.apiKey",
                        "claude.apiKey",
                        "claude.api_key",
                    ]:
                        value = _get_nested_value(config, key_path)
                        if value and isinstance(value, str):
                            os.environ["ANTHROPIC_API_KEY"] = value
                            break
                
                # Look for Cursor API key
                if not os.getenv("CURSOR_API_KEY"):
                    for key_path in [
                        "cursor.apiKey",
                        "cursor.api_key",
                        "cursorApiKey",
                        "cursor.token",
                    ]:
                        value = _get_nested_value(config, key_path)
                        if value and isinstance(value, str):
                            os.environ["CURSOR_API_KEY"] = value
                            break
        except (json.JSONDecodeError, IOError, KeyError):
            continue


def _get_nested_value(config: Dict[str, Any], key_path: str) -> Optional[str]:
    """Get a nested value from config dictionary using dot notation."""
    keys = key_path.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    return str(value) if value else None


# Provider registry
PROVIDERS: Dict[str, AIProvider] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "grok": GrokProvider,
    "mistral": MistralProvider,
    "cohere": CohereProvider,
    "perplexity": PerplexityProvider,
    "together": TogetherProvider,
    "deepseek": DeepSeekProvider,
    "cursor": CursorProvider,
}

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI (GPT)",
    "anthropic": "Anthropic (Claude)",
    "google": "Google (Gemini)",
    "grok": "xAI (Grok)",
    "mistral": "Mistral AI",
    "cohere": "Cohere",
    "perplexity": "Perplexity",
    "together": "Together AI",
    "deepseek": "DeepSeek",
    "cursor": "Cursor IDE",
}

# API Key Links for all providers
API_KEY_LINKS = {
    "openai": {
        "url": "https://platform.openai.com/api-keys",
        "billing": "https://platform.openai.com/account/billing",
        "env_var": "OPENAI_API_KEY",
        "description": "OpenAI GPT models (GPT-4, GPT-3.5, etc.)"
    },
    "anthropic": {
        "url": "https://console.anthropic.com/settings/keys",
        "billing": "https://console.anthropic.com/settings/billing",
        "env_var": "ANTHROPIC_API_KEY",
        "description": "Anthropic Claude models"
    },
    "google": {
        "url": "https://aistudio.google.com/app/apikey",
        "billing": "https://console.cloud.google.com/billing",
        "env_var": "GOOGLE_API_KEY",
        "description": "Google Gemini models"
    },
    "grok": {
        "url": "https://console.x.ai/api-keys",
        "billing": "https://console.x.ai/billing",
        "env_var": "XAI_API_KEY",
        "description": "xAI Grok models"
    },
    "mistral": {
        "url": "https://console.mistral.ai/api-keys",
        "billing": "https://console.mistral.ai/billing",
        "env_var": "MISTRAL_API_KEY",
        "description": "Mistral AI models"
    },
    "cohere": {
        "url": "https://dashboard.cohere.com/api-keys",
        "billing": "https://dashboard.cohere.com/billing",
        "env_var": "COHERE_API_KEY",
        "description": "Cohere models"
    },
    "perplexity": {
        "url": "https://www.perplexity.ai/settings/api",
        "billing": "https://www.perplexity.ai/settings/billing",
        "env_var": "PERPLEXITY_API_KEY",
        "description": "Perplexity AI models"
    },
    "together": {
        "url": "https://api.together.xyz/settings/api-keys",
        "billing": "https://api.together.xyz/settings/billing",
        "env_var": "TOGETHER_API_KEY",
        "description": "Together AI models"
    },
    "deepseek": {
        "url": "https://platform.deepseek.com/api_keys",
        "billing": "https://platform.deepseek.com/billing",
        "env_var": "DEEPSEEK_API_KEY",
        "description": "DeepSeek models"
    },
    "cursor": {
        "url": "https://cursor.com/dashboard",
        "billing": "https://cursor.com/settings/billing",
        "env_var": "CURSOR_API_KEY (or OPENAI_API_KEY/ANTHROPIC_API_KEY)",
        "description": "Cursor IDE (uses OpenAI/Anthropic internally)"
    },
}


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  Cursor AI - Multi-Provider Chat Interface")
    print("=" * 70)
    print()


def print_provider_selection() -> Optional[str]:
    """Display available providers and get user selection."""
    print("Available AI Providers:")
    print("-" * 70)
    
    available_providers = []
    for i, (key, provider_class) in enumerate(PROVIDERS.items(), 1):
        provider = provider_class()
        status = "✓" if provider.is_available() else "✗ (API key not set)"
        name = PROVIDER_DISPLAY_NAMES.get(key, key)
        print(f"  {i}) {name:25s} {status}")
        if provider.is_available():
            available_providers.append((i, key, name))
    
    print("-" * 70)
    
    if not available_providers:
        print("\n❌ No providers available. Please set API keys:")
        print("   Run: cursor_ai --get-keys  (to see all API key links)")
        print("\n   Quick links:")
        for key, info in API_KEY_LINKS.items():
            if key != "cursor":  # Skip cursor as it uses other keys
                print(f"   - {info['env_var']}: {info['url']}")
        return None
    
    while True:
        try:
            choice = input(f"\nSelect provider (1-{len(PROVIDERS)}) or name: ").strip().lower()
            
            # Try numeric selection
            if choice.isdigit():
                idx = int(choice)
                for num, key, name in available_providers:
                    if num == idx:
                        return key
            
            # Try name selection
            if choice in PROVIDERS:
                provider = PROVIDERS[choice]()
                if provider.is_available():
                    return choice
                else:
                    print(f"⚠️  {PROVIDER_DISPLAY_NAMES.get(choice, choice)} is not available (API key not set)")
                    continue
            
            # Try partial match
            for key in PROVIDERS:
                if key.lower() in choice or choice in key.lower():
                    provider = PROVIDERS[key]()
                    if provider.is_available():
                        return key
                    else:
                        print(f"⚠️  {PROVIDER_DISPLAY_NAMES.get(key, key)} is not available (API key not set)")
                        break
            
            print(f"Invalid selection. Please choose from available providers.")
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            return None


def print_help():
    """Print help message."""
    print("\nCommands:")
    print("  /help, /h       - Show this help message")
    print("  /switch, /s     - Switch to a different AI provider")
    print("  /clear, /c      - Clear conversation history")
    print("  /exit, /quit    - Exit the chat")
    print("  /model          - Show current model")
    print("  /providers      - List available providers")
    print()


def main():
    """Main chat loop."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="cursor_ai",
        description="Interactive chat with multiple AI providers",
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS.keys()),
        help="AI provider to use (default: interactive selection)",
    )
    parser.add_argument(
        "--model",
        help="Model to use (overrides default for provider)",
    )
    parser.add_argument(
        "--clear-history",
        action="store_true",
        help="Start with empty conversation history",
    )
    parser.add_argument(
        "--check-keys",
        action="store_true",
        help="Check which API keys are set and exit",
    )
    parser.add_argument(
        "--get-keys",
        action="store_true",
        help="Show links to get API keys for all providers",
    )
    
    args = parser.parse_args()
    
    # Show API key links mode
    if args.get_keys:
        print("\n" + "=" * 70)
        print("  API Keys - Quick Access Links")
        print("=" * 70)
        print("\n🔑 Direct Links to Get API Keys:\n")
        
        for i, (key, info) in enumerate(API_KEY_LINKS.items(), 1):
            provider_name = PROVIDER_DISPLAY_NAMES.get(key, key)
            print(f"{i}. {provider_name}:")
            print(f"   Description: {info['description']}")
            print(f"   Get API Key: {info['url']}")
            if 'billing' in info:
                print(f"   Billing: {info['billing']}")
            print(f"   Environment Variable: {info['env_var']}")
            print()
        
        print("-" * 70)
        print("\n💡 Quick Setup:")
        print("   Option 1: Export in your shell:")
        print("   export OPENAI_API_KEY='sk-your-key-here'")
        print("   export ANTHROPIC_API_KEY='sk-ant-your-key-here'")
        print("   source ~/.zshrc  # or ~/.bashrc")
        print("\n   Option 2: Create a .env file in project root:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        print("   ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print("   GOOGLE_API_KEY=your-google-key")
        print("   XAI_API_KEY=your-grok-key")
        print("   MISTRAL_API_KEY=your-mistral-key")
        print("   COHERE_API_KEY=your-cohere-key")
        print("   PERPLEXITY_API_KEY=your-perplexity-key")
        print("   TOGETHER_API_KEY=your-together-key")
        print("   DEEPSEEK_API_KEY=your-deepseek-key")
        print("\n" + "=" * 70 + "\n")
        return 0
    
    # Check keys mode
    if args.check_keys:
        print("\nAPI Key Status:")
        print("-" * 70)
        for key, ProviderClass in PROVIDERS.items():
            provider = ProviderClass()
            status = "✓ SET" if provider.is_available() else "✗ NOT SET"
            if key == "cursor":
                # Cursor provider uses OpenAI/Anthropic keys
                openai_avail = bool(os.getenv("OPENAI_API_KEY"))
                anthropic_avail = bool(os.getenv("ANTHROPIC_API_KEY"))
                if openai_avail or anthropic_avail:
                    status = "✓ SET"
                    env_info = "OPENAI_API_KEY" if openai_avail else "ANTHROPIC_API_KEY"
                    if openai_avail and anthropic_avail:
                        env_info = "OPENAI_API_KEY or ANTHROPIC_API_KEY"
                else:
                    status = "✗ NOT SET"
                    env_info = "OPENAI_API_KEY or ANTHROPIC_API_KEY"
            else:
                env_info = provider.api_key_env
            print(f"  {PROVIDER_DISPLAY_NAMES.get(key, key):25s} {status:10s} ({env_info})")
        print("-" * 70)
        
        # Check for .env file
        env_file = project_root / ".env"
        if env_file.exists():
            print(f"\n✓ .env file found at: {env_file}")
        else:
            print(f"\n⚠️  No .env file found. Create one in: {project_root}")
        print()
        return 0
    
    print_banner()
    
    # Select provider
    if args.provider:
        selected_key = args.provider
    else:
        selected_key = print_provider_selection()
        if not selected_key:
            return 1
    
    # Initialize provider
    ProviderClass = PROVIDERS[selected_key]
    provider = ProviderClass()
    
    if not provider.is_available():
        print(f"❌ {PROVIDER_DISPLAY_NAMES.get(selected_key, selected_key)} is not available.")
        print(f"   Please set {provider.api_key_env} environment variable.")
        return 1
    
    if not provider.initialize():
        return 1
    
    provider_name = PROVIDER_DISPLAY_NAMES.get(selected_key, selected_key)
    model_name = args.model or provider.default_model
    
    print(f"\n✓ Selected: {provider_name}")
    print(f"  Model: {model_name}")
    print("\nType your message (or /help for commands)")
    print("-" * 70)
    
    # Conversation history
    messages: List[Dict[str, str]] = []
    if not args.clear_history:
        # Optionally load from history file
        pass
    
    try:
        while True:
            try:
                # Get user input
                prompt = input(f"\n[{provider_name}] You: ").strip()
                
                if not prompt:
                    continue
                
                # Handle commands
                if prompt.startswith("/"):
                    cmd = prompt.lower().split()[0]
                    
                    if cmd in ("/exit", "/quit", "/q"):
                        print("\nGoodbye! 👋\n")
                        break
                    
                    elif cmd in ("/help", "/h"):
                        print_help()
                        continue
                    
                    elif cmd in ("/switch", "/s"):
                        new_key = print_provider_selection()
                        if new_key and new_key != selected_key:
                            ProviderClass = PROVIDERS[new_key]
                            provider = ProviderClass()
                            if provider.is_available() and provider.initialize():
                                selected_key = new_key
                                provider_name = PROVIDER_DISPLAY_NAMES.get(selected_key, selected_key)
                                model_name = args.model or provider.default_model
                                print(f"\n✓ Switched to: {provider_name}")
                                print(f"  Model: {model_name}")
                                if args.clear_history:
                                    messages = []
                        continue
                    
                    elif cmd in ("/clear", "/c"):
                        messages = []
                        print("✓ Conversation history cleared")
                        continue
                    
                    elif cmd == "/model":
                        print(f"\nProvider: {provider_name}")
                        print(f"Model: {model_name}")
                        continue
                    
                    elif cmd == "/providers":
                        print_provider_selection()
                        continue
                    
                    else:
                        print(f"Unknown command: {cmd}. Type /help for available commands.")
                        continue
                
                # Add user message
                messages.append({"role": "user", "content": prompt})
                
                # Get AI response
                print(f"\n[{provider_name}] Thinking...", end="", flush=True)
                
                try:
                    response = provider.chat(messages, model=args.model)
                    
                    # Print response
                    print(f"\r[{provider_name}] AI: {response}\n")
                except Exception as e:
                    print(f"\r❌ Error getting response: {e}\n")
                    if args.verbose:
                        import traceback
                        traceback.print_exc()
                    continue
                
                # Add AI response to history
                messages.append({"role": "assistant", "content": response})
                
                # Limit conversation history to prevent token overflow
                if len(messages) > 20:  # Keep last 10 exchanges
                    messages = messages[-20:]
                
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        print("\nChat session ended.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





