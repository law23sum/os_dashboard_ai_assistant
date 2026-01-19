#!/usr/bin/env python3
"""
Interactive terminal chat with multiple AI providers.

This script allows you to select and chat with different AI providers:
- OpenAI (GPT models)
- Anthropic (Claude)
- Google (Gemini)
- xAI (Grok)
- Cursor IDE
- ChatGPT Agents (via OpenAI)

Usage:
    cursor_ai
    cursor_ai --provider openai
    cursor_ai --help
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Sequence, Tuple
import json

# ==========================================
# API KEY CONFIGURATION & LINKS
# ==========================================
# You can set these directly here, or use environment variables (recommended)
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY", ""),
    "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
    "google": os.getenv("GOOGLE_API_KEY", ""),
    "xai": os.getenv("XAI_API_KEY", ""),  # Grok
    "cursor": os.getenv("CURSOR_API_KEY", ""),
}

API_LINKS = {
    "openai": "https://platform.openai.com/api-keys",
    "anthropic": "https://console.anthropic.com/settings/keys",
    "google": "https://aistudio.google.com/app/apikey",
    "xai": "https://console.x.ai/api-keys",
    "cursor": "https://cursor.com/dashboard",
}
# ==========================================

try:
    import readline  # For better input handling on Unix
except ImportError:
    readline = None

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

PROVIDER_KEY_LINKS: Dict[str, Dict[str, str]] = {
    # These are links to create/manage API keys (not keys themselves).
    "openai": {
        "keys": "https://platform.openai.com/api-keys",
        "docs": "https://platform.openai.com/docs",
        "billing": "https://platform.openai.com/account/billing",
    },
    "anthropic": {
        "keys": "https://console.anthropic.com/settings/keys",
        "docs": "https://docs.anthropic.com",
        "billing": "https://console.anthropic.com/settings/billing",
    },
    "google": {
        "keys": "https://aistudio.google.com/app/apikey",
        "docs": "https://ai.google.dev/docs",
    },
    "grok": {
        "keys": "https://console.x.ai/api-keys",
        "docs": "https://docs.x.ai",
    },
    "cursor": {
        "keys": "https://cursor.com/dashboard",
        "docs": "https://cursor.com/docs",
    },
}


def _iter_dotenv_candidates(root: Path) -> List[Path]:
    """
    Return an ordered list of .env-like files to load.
    We intentionally avoid reading arbitrary files and only check common names.
    """
    candidates: List[Path] = []
    # Common convention order: local overrides first, then base.
    for name in ("env.new", ".env.local", ".env", ".env.development", ".env.dev", ".env.production", ".env.prod"):
        candidates.append(root / name)
    return candidates


# Available models per provider (from env.new or defaults)
AVAILABLE_MODELS = {
    "openai": ["gpt-5.1", "gpt-5-mini", "o3-deep-research", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": ["claude-4.5-opus", "claude-4.5-sonnet", "claude-4.5-haiku", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
    "google": ["gemini-3-pro", "gemini-3-flash", "gemini-1.5-pro-latest", "gemini-2.5-flash"],
    "grok": ["grok-4", "grok-4-fast", "grok-beta"],
    "deepseek": ["deepseek-v3.2", "deepseek-r1", "deepseek-chat"],
    "groq": ["llama-4-scout", "qwen3-32b", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
    "cohere": ["command-r+", "command-r7b", "command-a", "command-r-plus"],
    "mistral": ["mistral-large-latest", "mistral-medium", "mistral-small"],
    "perplexity": ["sonar", "llama-3.1-sonar-large-128k-online"],
    "together": ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"],
}

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
        
        # Also load model lists if present
        if key == "OPENAI_MODELS" and value:
            AVAILABLE_MODELS["openai"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "ANTHROPIC_MODELS" and value:
            AVAILABLE_MODELS["anthropic"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "GOOGLE_MODELS" and value:
            AVAILABLE_MODELS["google"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "XAI_MODELS" and value:
            AVAILABLE_MODELS["grok"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "DEEPSEEK_MODELS" and value:
            AVAILABLE_MODELS["deepseek"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "GROQ_MODELS" and value:
            AVAILABLE_MODELS["groq"] = [m.strip() for m in value.split(",") if m.strip()]
        elif key == "COHERE_MODELS" and value:
            AVAILABLE_MODELS["cohere"] = [m.strip() for m in value.split(",") if m.strip()]


def load_from_shell_config() -> None:
    """Load environment variables from shell config files (.bashrc, .zshrc, etc.)."""
    home = Path.home()
    shell_config_files = [
        home / ".zshrc",      # Zsh (default on macOS)
        home / ".bashrc",     # Bash (Linux)
        home / ".bash_profile",  # Bash (macOS)
        home / ".profile",    # Generic profile
    ]
    
    for config_file in shell_config_files:
        if not config_file.exists():
            continue
        
        try:
            content = config_file.read_text(encoding='utf-8', errors='ignore')
            for line in content.splitlines():
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                
                # Match export statements: export VAR="value" or export VAR='value' or export VAR=value
                if line.startswith("export "):
                    # Remove 'export ' prefix
                    line = line[7:].strip()
                    if "=" not in line:
                        continue
                    
                    # Split on first = sign
                    parts = line.split("=", 1)
                    if len(parts) != 2:
                        continue
                    
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Only set if not already in environment (don't override existing)
                    if key and value and key not in os.environ:
                        # Skip placeholder values
                        if value in ["your-key-here", "sk-your-key-here", "your-openai-api-key"] or \
                           value.startswith("your-") or "placeholder" in value.lower():
                            continue
                        os.environ[key] = value
        except (IOError, UnicodeDecodeError):
            # Skip files that can't be read
            continue


# Load .env-like files from project root FIRST, before providers are initialized
for env_file in _iter_dotenv_candidates(project_root):
    if env_file.exists():
        load_dotenv(env_file)

# Also try loading from config module if it exists
try:
    from config.config import load_dotenv as config_load_dotenv
    config_load_dotenv()
except ImportError:
    pass

# Load from shell config files (.bashrc, .zshrc, etc.) as fallback
# This only sets variables that aren't already in the environment
load_from_shell_config()


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


class PerplexityProvider(AIProvider):
    """Perplexity AI provider."""
    
    def __init__(self):
        super().__init__("Perplexity AI", "PERPLEXITY_API_KEY")
        self.default_model = os.getenv("PERPLEXITY_MODEL", "sonar")
        self.base_url = "https://api.perplexity.ai"
    
    def initialize(self):
        # Perplexity uses OpenAI-compatible API
        pass


class ChatGPTAgentsProvider(OpenAIProvider):
    """ChatGPT Agents provider (specialized assistants)."""
    
    def __init__(self):
        super().__init__()
        self.name = "ChatGPT Agents"
        # We use the same key as OpenAI
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        # In a full implementation, this would connect to the Assistants API.
        # For now, we simulate agent behavior with system prompts if not already present.
        
        # Check if we need to inject a system prompt for specific agents if requested
        # (This is a simplified version of the full agents_ai script)
        return super().chat(messages, model)
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
            return "❌ Perplexity client not initialized"
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
    """Cohere provider."""
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
            user_message = ""
            
            prompt = messages[-1]["content"] if messages else ""
            
            for i in range(len(messages) - 1):
                msg = messages[i]
                if msg["role"] == "system":
                    continue  # Cohere handles system context differently
                elif msg["role"] == "user":
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


class MistralProvider(AIProvider):
    """Mistral AI provider."""
    
    def __init__(self):
        super().__init__("Mistral AI", "MISTRAL_API_KEY")
        self.default_model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        self.base_url = "https://api.mistral.ai/v1"
    
    def initialize(self):
        # Mistral uses OpenAI-compatible API
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
                messages=messages
            )
            return response.choices[0].message.content
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


class DeepSeekProvider(AIProvider):
    """DeepSeek provider."""
    
    def __init__(self):
        super().__init__("DeepSeek", "DEEPSEEK_API_KEY")
        self.default_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = "https://api.deepseek.com/v1"
    
    def initialize(self):
        # DeepSeek uses OpenAI-compatible API
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
                messages=messages
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
            return "❌ DeepSeek client not initialized"
            return "❌ Together AI client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"


class GroqProvider(AIProvider):
    """Groq provider (fast inference)."""
    
    def __init__(self):
        super().__init__("Groq", "GROQ_API_KEY")
        self.default_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        self.base_url = "https://api.groq.com/openai/v1"
    
    def initialize(self):
        # Groq uses OpenAI-compatible API
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
            return "❌ Groq client not initialized"
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages
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
            return "❌ Groq client not initialized"
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
    "perplexity": PerplexityProvider,
    "cohere": CohereProvider,
    "mistral": MistralProvider,
    "deepseek": DeepSeekProvider,
    "groq": GroqProvider,
    "mistral": MistralProvider,
    "cohere": CohereProvider,
    "perplexity": PerplexityProvider,
    "together": TogetherProvider,
    "deepseek": DeepSeekProvider,
    "cursor": CursorProvider,
    "agents": ChatGPTAgentsProvider,
}

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI (GPT)",
    "anthropic": "Anthropic (Claude)",
    "google": "Google (Gemini)",
    "grok": "xAI (Grok)",
    "perplexity": "Perplexity AI",
    "cohere": "Cohere",
    "mistral": "Mistral AI",
    "deepseek": "DeepSeek",
    "groq": "Groq (Fast Inference)",
    "mistral": "Mistral AI",
    "cohere": "Cohere",
    "perplexity": "Perplexity",
    "together": "Together AI",
    "deepseek": "DeepSeek",
    "cursor": "Cursor IDE",
    "agents": "ChatGPT Agents",
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
        models = AVAILABLE_MODELS.get(key, [])
        model_info = f" [{models[0]}]" if models and provider.is_available() else ""
        print(f"  {i}) {name:25s} {status}{model_info}")
        if provider.is_available():
            available_providers.append((i, key, name))
    
    print("-" * 70)
    
    if not available_providers:
        print("\n❌ No providers available. Please set API keys:")
        print("   - OPENAI_API_KEY for OpenAI (GPT)")
        print("   - ANTHROPIC_API_KEY for Anthropic (Claude)")
        print("   - GOOGLE_API_KEY for Google (Gemini)")
        print("   - XAI_API_KEY for xAI (Grok)")
        print("   - PERPLEXITY_API_KEY for Perplexity AI")
        print("   - COHERE_API_KEY for Cohere")
        print("   - MISTRAL_API_KEY for Mistral AI")
        print("   - DEEPSEEK_API_KEY for DeepSeek")
        print("   - GROQ_API_KEY for Groq")
        print("\n📚 See API_KEYS_GUIDE.md for links to get API keys")
        print("   Or run: python cursor_ai.py --get-keys")
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


def print_models_for_provider(provider_key: str) -> None:
    """Print available models for a provider."""
    models = AVAILABLE_MODELS.get(provider_key, [])
    if not models:
        print(f"\n⚠️  No models configured for {provider_key}")
        return
    
    print(f"\nAvailable models for {PROVIDER_DISPLAY_NAMES.get(provider_key, provider_key)}:")
    print("-" * 70)
    for i, model in enumerate(models, 1):
        print(f"  {i}) {model}")
    print("-" * 70)


def select_model(provider_key: str, current_model: str) -> Optional[str]:
    """Interactive model selection for a provider."""
    models = AVAILABLE_MODELS.get(provider_key, [])
    if not models:
        print(f"\n⚠️  No models configured for {provider_key}")
        return None
    
    print(f"\nCurrent model: {current_model}")
    print_models_for_provider(provider_key)
    
    while True:
        try:
            choice = input(f"\nSelect model (1-{len(models)}) or name [current]: ").strip()
            if not choice:
                return current_model
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
            
            # Try name match
            for model in models:
                if choice.lower() in model.lower() or model.lower() in choice.lower():
                    return model
            
            print(f"Invalid selection. Please choose 1-{len(models)} or a model name.")
        except (EOFError, KeyboardInterrupt):
            return current_model


def print_all_models() -> None:
    """Print all available models for all providers."""
    print("\n" + "=" * 70)
    print("  Available Models by Provider")
    print("=" * 70)
    
    for provider_key in sorted(PROVIDERS.keys()):
        models = AVAILABLE_MODELS.get(provider_key, [])
        if models:
            provider_name = PROVIDER_DISPLAY_NAMES.get(provider_key, provider_key)
            print(f"\n{provider_name}:")
            for model in models:
                print(f"  • {model}")


def print_help():
    """Print help message."""
    print("\nCommands:")
    print("  /help, /h       - Show this help message")
    print("  /switch, /s     - Switch to a different AI provider")
    print("  /clear, /c      - Clear conversation history")
    print("  /exit, /quit    - Exit the chat")
    print("  /model          - Show current model")
    print("  /models         - List all available models")
    print("  /setmodel       - Change model for current provider")
    print("  /providers      - List available providers")
    print("  /compare        - Compare responses from multiple models")
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
        print("1. OpenAI (GPT models):")
        print("   https://platform.openai.com/api-keys")
        print("   Billing: https://platform.openai.com/account/billing")
        print("\n2. Anthropic (Claude):")
        print("   https://console.anthropic.com/settings/keys")
        print("   Billing: https://console.anthropic.com/settings/billing")
        print("\n3. Google (Gemini):")
        print("   https://aistudio.google.com/app/apikey")
        print("\n4. xAI (Grok):")
        print("   https://console.x.ai/api-keys")
        print("\n5. Perplexity AI:")
        print("   https://www.perplexity.ai/settings/api")
        print("\n6. Cohere:")
        print("   https://dashboard.cohere.com/api-keys")
        print("\n7. Mistral AI:")
        print("   https://console.mistral.ai/api-keys/")
        print("\n8. DeepSeek:")
        print("   https://platform.deepseek.com/api_keys")
        print("\n9. Groq (Fast Inference):")
        print("   https://console.groq.com/keys")
        print("\n10. Cursor IDE:")
        print("   https://cursor.com/dashboard")
        print("   (Note: For chat, use OpenAI/Anthropic keys instead)")
        print("\n" + "-" * 70)
        
        for name, link in API_LINKS.items():
            print(f"{name.capitalize()}:")
            print(f"   {link}")
            if name == "openai":
                print("   Billing: https://platform.openai.com/account/billing")
            elif name == "anthropic":
                print("   Billing: https://console.anthropic.com/settings/billing")
            print()
            
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
        print("   export ANTHROPIC_API_KEY='sk-ant-REDACTED'")
        print("   source ~/.zshrc  # or ~/.bashrc")
        print("\n   Option 2: Create a .env file in project root:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        print("   ANTHROPIC_API_KEY=sk-ant-REDACTED")
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
                        print_models_for_provider(selected_key)
                        continue
                    
                    elif cmd == "/models":
                        print_all_models()
                        continue
                    
                    elif cmd == "/setmodel":
                        new_model = select_model(selected_key, model_name)
                        if new_model and new_model != model_name:
                            model_name = new_model
                            print(f"\n✓ Model changed to: {model_name}")
                        continue
                    
                    elif cmd == "/compare":
                        print("\n🔍 Model Comparison Mode")
                        print("Enter your prompt, then select models to compare:")
                        compare_prompt = input("\nYour prompt: ").strip()
                        if not compare_prompt:
                            print("No prompt entered.")
                            continue
                        
                        print("\nSelect models to compare (comma-separated numbers or names):")
                        print_models_for_provider(selected_key)
                        model_choices = input("Models: ").strip()
                        
                        if not model_choices:
                            continue
                        
                        # Parse model selections
                        models_to_compare = []
                        models = AVAILABLE_MODELS.get(selected_key, [])
                        for choice in model_choices.split(","):
                            choice = choice.strip()
                            if choice.isdigit():
                                idx = int(choice) - 1
                                if 0 <= idx < len(models):
                                    models_to_compare.append(models[idx])
                            else:
                                for model in models:
                                    if choice.lower() in model.lower():
                                        models_to_compare.append(model)
                                        break
                        
                        if not models_to_compare:
                            print("No valid models selected.")
                            continue
                        
                        # Compare responses
                        print(f"\n{'='*70}")
                        print(f"Comparing {len(models_to_compare)} model(s) with prompt:")
                        print(f"'{compare_prompt}'")
                        print(f"{'='*70}\n")
                        
                        compare_messages = [{"role": "user", "content": compare_prompt}]
                        for model in models_to_compare:
                            print(f"\n[{model}]")
                            print("-" * 70)
                            try:
                                response = provider.chat(compare_messages, model=model)
                                print(response)
                            except Exception as e:
                                print(f"❌ Error: {e}")
                            print()
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







