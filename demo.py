#!/usr/bin/env python3
"""
Simple demo of Policy Enforcer without requiring OpenAI API key.
This demonstrates the business rules engine and state management.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from policy_enforcer.state import get_state, reset_state, WeatherCondition, Activity
from policy_enforcer.rules import get_rule_engine
from policy_enforcer.tools import get_tools


def print_banner():
    """Print demo banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                 Policy Enforcer Demo                      ║
║            Business Rules Engine Showcase                 ║
╚═══════════════════════════════════════════════════════════╝

This demo shows how business rules are enforced without an LLM.
""")


def demo_business_rules():
    """Demonstrate business rules enforcement."""
    print("🧪 Business Rules Enforcement Demo\n")
    
    # Reset state
    reset_state()
    state = get_state()
    rule_engine = get_rule_engine()
    tools = get_tools()
    
    print("📜 Current Business Rules:")
    print(rule_engine.get_rules_summary())
    
    print("\n📊 Initial State:")
    print(state.get_summary())
    
    print("\n" + "="*60)
    print("SCENARIO 1: Trying to play games without equipment")
    print("="*60)
    
    # Try to choose activity without required items
    activity_tool = next(tool for tool in tools if tool.name == "choose_activity")
    result = activity_tool.run({"activity": "Play games"})
    print(f"Result: {result}")
    
    print("\n" + "="*60)
    print("SCENARIO 2: Shopping for required items")
    print("="*60)
    
    shopping_tool = next(tool for tool in tools if tool.name == "shopping")
    
    print("Buying TV...")
    result = shopping_tool.run({"item": "TV"})
    print(f"Result: {result}")
    
    print("Buying Xbox...")
    result = shopping_tool.run({"item": "Xbox"})
    print(f"Result: {result}")
    
    print(f"\nUpdated inventory: {list(state.inventory)}")
    
    print("\n" + "="*60)
    print("SCENARIO 3: Now trying to play games with equipment")
    print("="*60)
    
    result = activity_tool.run({"activity": "Play games"})
    print(f"Result: {result}")
    
    print("\n" + "="*60)
    print("SCENARIO 4: Weather-dependent activities")
    print("="*60)
    
    # Check weather
    weather_tool = next(tool for tool in tools if tool.name == "check_weather")
    print("Checking weather...")
    result = weather_tool.run({})
    print(f"Result: {result}")
    print(f"Weather is now: {state.weather.value}")
    
    # Try camping based on weather
    print("\nBuying hiking boots...")
    result = shopping_tool.run({"item": "Hiking Boots"})
    print(f"Result: {result}")
    
    print("\nTrying to go camping...")
    result = activity_tool.run({"activity": "Go Camping"})
    print(f"Result: {result}")
    
    print("\n" + "="*60)
    print("SCENARIO 5: Trying to check weather again (should fail)")
    print("="*60)
    
    result = weather_tool.run({})
    print(f"Result: {result}")
    
    print("\n📊 Final State:")
    print(state.get_summary())


def demo_state_management():
    """Demonstrate state management features."""
    print("\n🔄 State Management Demo\n")
    
    reset_state()
    state = get_state()
    
    print("Adding items to inventory...")
    state.add_to_inventory("Goggles")
    state.add_to_inventory("Sunscreen")
    
    print(f"Has Goggles: {state.has_item('Goggles')}")
    print(f"Has Swimming gear: {state.has_items(['Goggles'])}")
    print(f"Has Gaming gear: {state.has_items(['TV', 'Xbox'])}")
    
    print("\nSetting weather to snowy...")
    state.set_weather(WeatherCondition.SNOWING)
    
    print(f"Weather: {state.weather.value}")
    print(f"Weather checked: {state.weather_checked}")
    
    print(f"\nShopping history: {state.shopping_history}")
    print(f"Current inventory: {list(state.inventory)}")


def main():
    """Run the complete demo."""
    print_banner()
    
    try:
        demo_business_rules()
        demo_state_management()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\nTo use the full ReAct agent with OpenAI:")
        print(f"1. Set OPENAI_API_KEY in .env file")
        print(f"2. Run: python main.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
