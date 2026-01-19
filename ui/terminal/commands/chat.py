"""Interactive chat command handler."""

from __future__ import annotations

import sys
from typing import Optional

try:
    import readline  # For better input handling on Unix
except ImportError:
    readline = None  # Windows doesn't have readline

from assistant_core.ai import (
    generate_ai_reply,
    AGENT_MODELS,
    DEFAULT_MODEL,
    INTERACTION_STYLES,
    normalize_interaction_style,
)
from assistant_hub.db import (
    CHAT_PERSONAS,
    GENERIC_AI_PERSONAS,
    GENERIC_AI_PROVIDERS,
    PERSONAL_AI_PERSONAS,
    ChatMessage,
    init_db,
    db_insert_chat_message,
    load_state,
)


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  AI OS Console - Interactive Terminal Chat")
    print("=" * 70)
    print()


def _default_provider_for(agent: str) -> str:
    if agent in GENERIC_AI_PERSONAS:
        return GENERIC_AI_PROVIDERS.get(agent, "openai")
    return "openai"


def _describe_model(agent: str, provider: str) -> str:
    if agent in PERSONAL_AI_PERSONAS:
        return AGENT_MODELS.get(agent, DEFAULT_MODEL)
    if provider == "openai":
        return DEFAULT_MODEL
    return "provider default"


def _build_agent_options():
    personal_descriptions = {
        "Chris": "Cost-optimized default chat",
        "AIC": "Deep reasoning / agentic control",
        "Aria": "Coding + content polish",
        "Sora": "Complex reasoning + planning",
        "Gabriela": "Commercialization strategy",
    }
    generic_descriptions = {
        "ChatGPT": "Generic ChatGPT (OpenAI)",
        "Claude": "Generic Claude (Anthropic)",
        "Gemini": "Generic Gemini (Google)",
        "DeepSeek": "Generic DeepSeek",
        "Grok": "Generic Grok (xAI)",
        "Cohere": "Generic Cohere",
        "Groq": "Generic Groq",
    }
    personal = []
    if "Chris" in CHAT_PERSONAS and "Chris" not in PERSONAL_AI_PERSONAS:
        personal.append(
            {
                "name": "Chris",
                "provider": "openai",
                "description": personal_descriptions.get("Chris", ""),
                "category": "personal",
            }
        )
    for persona in PERSONAL_AI_PERSONAS:
        personal.append(
            {
                "name": persona,
                "provider": "openai",
                "description": personal_descriptions.get(persona, ""),
                "category": "personal",
            }
        )
    generic = []
    for persona in GENERIC_AI_PERSONAS:
        generic.append(
            {
                "name": persona,
                "provider": _default_provider_for(persona),
                "description": generic_descriptions.get(persona, ""),
                "category": "generic",
            }
        )
    return personal, generic


def print_ai_selection():
    """Display available AI agents and get user selection."""
    print("Available AI Agents:")
    print("-" * 70)

    personal, generic = _build_agent_options()
    options = personal + generic
    index = 1

    if personal:
        print("Personal Agents:")
        for option in personal:
            desc = f" - {option['description']}" if option["description"] else ""
            print(f"  {index}) {option['name']:8s}{desc}")
            index += 1

    if generic:
        print("Generic Models:")
        for option in generic:
            desc = f" - {option['description']}" if option["description"] else ""
            print(f"  {index}) {option['name']:8s}{desc}")
            index += 1

    print("-" * 70)

    while True:
        try:
            choice = input(f"\nSelect AI agent (1-{len(options)}) or name: ").strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    selected = options[idx]
                    return selected["name"], selected["provider"]

            for option in options:
                if option["name"].lower() == choice.lower():
                    return option["name"], option["provider"]

            names = ", ".join(opt["name"] for opt in options)
            print(f"Invalid selection. Please choose 1-{len(options)} or one of: {names}")
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            sys.exit(0)


def print_help():
    """Print help message."""
    print("\nCommands:")
    print("  /help, /h     - Show this help message")
    print("  /switch, /s   - Switch to a different AI agent")
    print("  /clear, /c    - Clear conversation history")
    print("  /exit, /quit  - Exit the chat")
    print("  /model        - Show current AI model")
    print("  /provider, /p - Switch AI provider (OpenAI, Anthropic, etc.)")
    print("  /style, /mode - Set interaction style (discussion, debate, informative, persuasive)")
    print()


def print_provider_selection():
    """Display available AI providers and get user selection."""
    providers = [
        "openai", "anthropic", "google", "xai", 
        "cohere", "deepseek", "groq"
    ]
    
    print("\nAvailable AI Providers:")
    print("-" * 70)
    for i, p in enumerate(providers, 1):
        print(f"  {i}) {p}")
    print("-" * 70)
    
    while True:
        try:
            choice = input("\nSelect Provider (1-7) or name [openai]: ").strip().lower()
            if not choice:
                return "openai"
                
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(providers):
                    return providers[idx]
            
            if choice in providers:
                return choice
                
            print(f"Invalid selection. Please choose 1-{len(providers)}")
        except (EOFError, KeyboardInterrupt):
            return "openai"


def print_style_selection(current: Optional[str]) -> Optional[str]:
    """Display available interaction styles and return selection."""
    print("\nAvailable Interaction Styles:")
    print("-" * 70)
    for key, description in INTERACTION_STYLES.items():
        marker = "*" if current == key else " "
        print(f" {marker} {key:11s} - {description}")
    print("-" * 70)

    while True:
        try:
            choice = input("\nSelect style (blank to clear): ").strip()
            if not choice:
                return None
            normalized = normalize_interaction_style(choice)
            if normalized:
                return normalized
            valid = ", ".join(sorted(INTERACTION_STYLES.keys()))
            print(f"Invalid style. Choose one of: {valid}")
        except (EOFError, KeyboardInterrupt):
            return current


def handle_chat_command(args) -> int:
    """Handle the interactive chat command."""
    print_banner()
    
    # Initialize database
    conn = init_db()
    
    # Select initial AI agent
    selected_agent = None
    selected_provider = "openai"
    interaction_style = normalize_interaction_style(getattr(args, "style", None))
    if args.agent and args.agent in CHAT_PERSONAS:
        selected_agent = args.agent
        selected_provider = _default_provider_for(selected_agent)
    else:
        selected_agent, selected_provider = print_ai_selection()
    
    print(f"\n✓ Selected AI: {selected_agent}")
    print(f"  Model: {_describe_model(selected_agent, selected_provider)}")
    print(f"  Provider: {selected_provider}")
    if interaction_style:
        print(f"  Style: {interaction_style}")
    print("\nType your message (or /help for commands)")
    print("-" * 70)
    
    # Load conversation history
    state = load_state(conn)
    history = state.chat_messages.copy()
    
    # Filter history to current agent if needed
    if args.clear_history:
        history = []
    
    try:
        while True:
            try:
                # Get user input
                prompt = input(f"\n[{selected_agent}] You: ").strip()
                
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
                        new_agent, new_provider = print_ai_selection()
                        if new_agent != selected_agent or new_provider != selected_provider:
                            selected_agent = new_agent
                            selected_provider = new_provider
                            print(f"\n✓ Switched to: {selected_agent}")
                            print(f"  Model: {_describe_model(selected_agent, selected_provider)}")
                            print(f"  Provider: {selected_provider}")
                            # Optionally clear history when switching
                            if args.clear_on_switch:
                                history = []
                        continue
                    
                    elif cmd in ("/clear", "/c"):
                        history = []
                        print("✓ Conversation history cleared")
                        continue
                    
                    elif cmd == "/model":
                        print(f"\nCurrent AI: {selected_agent}")
                        print(f"Model: {_describe_model(selected_agent, selected_provider)}")
                        print(f"Provider: {selected_provider}")
                        continue

                    elif cmd in ("/provider", "/p"):
                        new_provider = print_provider_selection()
                        if new_provider != selected_provider:
                            selected_provider = new_provider
                            print(f"\n✓ Switched to Provider: {selected_provider}")
                        continue

                    elif cmd in ("/style", "/mode", "/interaction"):
                        interaction_style = print_style_selection(interaction_style)
                        if interaction_style:
                            print(f"\n✓ Interaction style: {interaction_style}")
                        else:
                            print("\n✓ Interaction style cleared")
                        continue
                    
                    else:
                        print(f"Unknown command: {cmd}. Type /help for available commands.")
                        continue
                
                # Store user message
                user_msg = ChatMessage(
                    id=0,
                    persona=selected_agent,
                    role="user",
                    content=prompt,
                )
                history.append(user_msg)
                
                # Save to database
                db_insert_chat_message(conn, user_msg)
                
                # Get AI response
                print(f"\n[{selected_agent} via {selected_provider}] Thinking...", end="", flush=True)
                
                reply, error, tool_calls = generate_ai_reply(
                    history,
                    persona=selected_agent,
                    prompt=prompt,
                    enable_shell=args.enable_shell,
                    model_provider=selected_provider,
                    interaction_style=interaction_style,
                )
                
                if error:
                    print(f"\n❌ Error: {error}")
                    continue
                
                # Store AI response
                ai_msg = ChatMessage(
                    id=0,
                    persona=selected_agent,
                    role="assistant",
                    content=reply,
                )
                history.append(ai_msg)
                db_insert_chat_message(conn, ai_msg)
                
                # Print response
                print(f"\r[{selected_agent}] AI: {reply}\n")
                
                # Handle tool calls if any
                if tool_calls:
                    print(f"  [Tool calls: {len(tool_calls)}]")
                
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                if args.verbose:
                    traceback.print_exc()
    
    finally:
        conn.close()
    
    return 0
