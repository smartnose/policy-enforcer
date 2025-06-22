#!/usr/bin/env python3
"""
Policy Enforcer CLI - ReAct Agent Demo with Business Rule Enforcement
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

from policy_enforcer.agents import create_agent
from policy_enforcer.state import get_state, reset_state
from policy_enforcer.rules import get_rule_engine


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                    Policy Enforcer Demo                   ║
║              ReAct Agent with Business Rules              ║
║                   Powered by Gemini 1.5 Flash            ║
╚═══════════════════════════════════════════════════════════╝

This demo showcases a ReAct agent that enforces business rules
when helping users choose activities using Google's Gemini model.

Available activities: Play games, Go Camping, Swimming
Type 'help' for available commands.
"""
    print(banner)


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  help              - Show this help message
  rules             - Show current business rules
  state             - Show current agent state
  reset             - Reset agent state
  quit/exit         - Exit the application
  
  Or simply type your request to interact with the agent!
  
Examples:
  "I want to go camping"
  "Check the weather"
  "Buy hiking boots"
  "What activities can I do?"
"""
    print(help_text)


def setup_environment() -> bool:
    """Setup environment variables and check requirements."""
    # Load environment variables from .env file in the project root
    load_dotenv()
    
    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your Google API key in a .env file or environment variable.")
        print("Example: export GOOGLE_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ Google API key loaded successfully (length: {len(api_key)} chars)")
    return True


def main():
    """Main CLI application."""
    print_banner()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create agent
    print("🚀 Initializing ReAct agent...")
    try:
        agent = create_agent()
        print("✅ Agent initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Main interaction loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'rules':
                print("📜 " + agent.show_rules())
                continue
            elif user_input.lower() == 'state':
                print(agent.show_state())
                continue
            elif user_input.lower() == 'reset':
                agent.reset()
                continue
            
            # Process user input with agent
            print("🤖 Agent: Thinking...")
            response = agent.run(user_input)
            print(f"🤖 Agent: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Type 'help' for available commands.")


if __name__ == "__main__":
    main()
