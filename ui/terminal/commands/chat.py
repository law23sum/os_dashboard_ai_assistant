"""Interactive chat command handler."""

from __future__ import annotations

import sys
from typing import Optional

try:
    import readline  # For better input handling on Unix
except ImportError:
    readline = None  # Windows doesn't have readline

from assistant_core.ai import generate_ai_reply, AGENT_MODELS
from assistant_hub.db import PERSONAS, ChatMessage, init_db, db_insert_chat_message, load_state


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  OS Dashboard AI Assistant - Interactive Terminal Chat")
    print("=" * 70)
    print()


def print_ai_selection():
    """Display available AI agents and get user selection."""
    print("Available AI Agents:")
    print("-" * 70)
    
    agent_descriptions = {
        "AIC": "Deep reasoning / agentic control (gpt-5.2-pro)",
        "Aria": "Coding + content polish (gpt-5.1-codex-max)",
        "Sora": "Complex reasoning + planning (gpt-5.2)",
        "Chris": "Cost-optimized default chat (gpt-5-mini)",
    }
    
    for i, persona in enumerate(PERSONAS, 1):
        desc = agent_descriptions.get(persona, "")
        print(f"  {i}) {persona:8s} - {desc}")
    
    print("-" * 70)
    
    while True:
        try:
            choice = input("\nSelect AI agent (1-4) or name: ").strip()
            
            # Try numeric selection
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(PERSONAS):
                    return PERSONAS[idx]
            
            # Try name selection
            if choice in PERSONAS:
                return choice
            
            # Try case-insensitive match
            for persona in PERSONAS:
                if persona.lower() == choice.lower():
                    return persona
            
            print(f"Invalid selection. Please choose 1-4 or one of: {', '.join(PERSONAS)}")
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
    print()


def handle_chat_command(args) -> int:
    """Handle the interactive chat command."""
    print_banner()
    
    # Initialize database
    conn = init_db()
    
    # Select initial AI agent
    selected_agent = None
    if args.agent and args.agent in PERSONAS:
        selected_agent = args.agent
    else:
        selected_agent = print_ai_selection()
    
    print(f"\n✓ Selected AI: {selected_agent}")
    print(f"  Model: {AGENT_MODELS.get(selected_agent, 'gpt-5-mini')}")
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
                        new_agent = print_ai_selection()
                        if new_agent != selected_agent:
                            selected_agent = new_agent
                            print(f"\n✓ Switched to: {selected_agent}")
                            print(f"  Model: {AGENT_MODELS.get(selected_agent, 'gpt-5-mini')}")
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
                        print(f"Model: {AGENT_MODELS.get(selected_agent, 'gpt-5-mini')}")
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
                print(f"\n[{selected_agent}] Thinking...", end="", flush=True)
                
                reply, error, tool_calls = generate_ai_reply(
                    history,
                    persona=selected_agent,
                    prompt=prompt,
                    enable_shell=args.enable_shell,
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





