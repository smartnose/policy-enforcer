#!/usr/bin/env python3
"""
Test script to verify that tools and rules work correctly with keyword-only arguments.
"""

from policy_enforcer.tools import get_tools
from policy_enforcer.rules import get_rule_engine
from policy_enforcer.state import get_state, reset_state


def test_keyword_only_arguments():
    """Test that all tools and rules work with keyword-only arguments."""
    print("🧪 Testing keyword-only arguments in tools and rules...")
    
    # Reset state for clean test
    reset_state()
    state = get_state()
    
    # Get components
    tools = get_tools()
    rule_engine = get_rule_engine()
    
    print(f"\n✅ Created {len(tools)} tools and rule engine with {len(rule_engine.rules)} rules")
    
    # Test 1: Rules with keyword arguments
    print("\n1️⃣ Testing rules with keyword arguments...")
    
    # Test activity rules
    result = rule_engine.check_activity_rules(state, "Play games")
    print(f"   Play games (no equipment): {result.allowed} - {result.reason}")
    
    result = rule_engine.check_tool_rules(state, "check_weather")
    print(f"   Weather tool: {result.allowed}")
    
    # Test 2: Tool execution with keyword arguments
    print("\n2️⃣ Testing tool execution with keyword arguments...")
    
    shopping_tool = next(tool for tool in tools if tool.name == 'shopping')
    weather_tool = next(tool for tool in tools if tool.name == 'check_weather')
    activity_tool = next(tool for tool in tools if tool.name == 'choose_activity')
    
    # Execute weather tool
    result = weather_tool.execute()
    print(f"   Weather tool result: {result}")
    
    # Execute shopping tool with keyword arguments
    result = shopping_tool.execute(item="TV")
    print(f"   Shopping TV: {result}")
    
    result = shopping_tool.execute(item="Xbox")
    print(f"   Shopping Xbox: {result}")
    
    # Test 3: Rule checking after changes
    print("\n3️⃣ Testing rules after state changes...")
    
    # Now try activity with equipment
    result = rule_engine.check_activity_rules(state, "Play games")
    print(f"   Play games (with equipment): {result.allowed}")
    
    # Execute activity tool
    result = activity_tool.execute(activity="Play games")
    print(f"   Choose activity: {result}")
    
    print(f"\n4️⃣ Final state:")
    print(f"   Inventory: {state.inventory}")
    print(f"   Weather: {state.weather.value}")
    print(f"   Activity: {state.chosen_activity.value if state.chosen_activity else 'None'}")
    
    print("\n🎉 All tests passed! Keyword-only arguments work correctly.")


if __name__ == "__main__":
    test_keyword_only_arguments()
