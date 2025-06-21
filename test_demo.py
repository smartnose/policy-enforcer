#!/usr/bin/env python3
"""
Test script for Policy Enforcer demo.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from policy_enforcer.state import get_state, reset_state, WeatherCondition, Activity
from policy_enforcer.rules import get_rule_engine
from policy_enforcer.tools import get_tools


def test_state_management():
    """Test the state management system."""
    print("🧪 Testing State Management...")
    
    # Reset state
    reset_state()
    state = get_state()
    
    # Test initial state
    assert state.inventory == set()
    assert state.weather == WeatherCondition.UNKNOWN
    assert state.weather_checked == False
    assert state.chosen_activity is None
    
    # Test adding items
    state.add_to_inventory("TV")
    state.add_to_inventory("Xbox")
    assert state.has_item("TV")
    assert state.has_item("Xbox")
    assert state.has_items(["TV", "Xbox"])
    
    # Test weather setting
    state.set_weather(WeatherCondition.SUNNY)
    assert state.weather == WeatherCondition.SUNNY
    assert state.weather_checked == True
    
    # Test activity setting
    state.set_activity(Activity.PLAY_GAMES)
    assert state.chosen_activity == Activity.PLAY_GAMES
    
    print("✅ State management tests passed!")


def test_business_rules():
    """Test the business rules engine."""
    print("🧪 Testing Business Rules...")
    
    rule_engine = get_rule_engine()
    reset_state()
    state = get_state()
    
    # Test play games rule - should fail without equipment
    result = rule_engine.check_activity_rules(state, Activity.PLAY_GAMES.value)
    assert not result.allowed
    assert "TV" in result.reason and "Xbox" in result.reason
    
    # Add equipment and test again
    state.add_to_inventory("TV")
    state.add_to_inventory("Xbox")
    result = rule_engine.check_activity_rules(state, Activity.PLAY_GAMES.value)
    assert result.allowed
    
    # Test camping weather rule
    state.set_weather(WeatherCondition.RAINING)
    result = rule_engine.check_activity_rules(state, Activity.GO_CAMPING.value)
    assert not result.allowed
    assert "raining" in result.reason.lower()
    
    # Test unknown weather rule
    state.set_weather(WeatherCondition.UNKNOWN)
    result = rule_engine.check_activity_rules(state, Activity.GO_CAMPING.value)
    assert not result.allowed
    assert "unknown" in result.reason.lower()
    
    # Test weather check rule
    state.set_weather(WeatherCondition.SUNNY)
    result = rule_engine.check_tool_rules(state, "check_weather")
    assert not result.allowed
    assert "already been checked" in result.reason
    
    print("✅ Business rules tests passed!")


def test_tools():
    """Test the tools functionality."""
    print("🧪 Testing Tools...")
    
    tools = get_tools()
    assert len(tools) == 3
    
    tool_names = [tool.name for tool in tools]
    assert "check_weather" in tool_names
    assert "shopping" in tool_names
    assert "choose_activity" in tool_names
    
    print("✅ Tools tests passed!")


def test_integration():
    """Test integration between components."""
    print("🧪 Testing Integration...")
    
    reset_state()
    state = get_state()
    tools = get_tools()
    
    # Get shopping tool
    shopping_tool = next(tool for tool in tools if tool.name == "shopping")
    
    # Test shopping tool execution
    result = shopping_tool.run(item="Hiking Boots")
    assert "Successfully purchased: Hiking Boots" in result
    assert state.has_item("Hiking Boots")
    
    # Get weather tool
    weather_tool = next(tool for tool in tools if tool.name == "check_weather")
    
    # Test weather tool execution
    result = weather_tool.run()
    assert "Weather check complete" in result
    assert state.weather_checked
    
    # Try to check weather again (should fail)
    result = weather_tool.run()
    assert "Rule violation" in result
    
    print("✅ Integration tests passed!")


def main():
    """Run all tests."""
    print("🚀 Running Policy Enforcer Tests...\n")
    
    try:
        test_state_management()
        print()
        
        test_business_rules()
        print()
        
        test_tools()
        print()
        
        test_integration()
        print()
        
        print("🎉 All tests passed! The Policy Enforcer demo is ready to use.")
        print("\nTo run the demo, execute: python main.py")
        print("Make sure to set your OPENAI_API_KEY in a .env file first.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
