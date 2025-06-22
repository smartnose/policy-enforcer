"""
Integration tests for the Policy Enforcer system.
"""

import unittest
from policy_enforcer.tools import get_tools
from policy_enforcer.rules import get_rule_engine
from policy_enforcer.state import get_state, reset_state
from policy_enforcer.items import Item


class TestSystemIntegration(unittest.TestCase):
    """Test integration between different system components."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_state()
        self.tools = get_tools()
        self.rule_engine = get_rule_engine()
        self.state = get_state()
    
    def test_complete_gaming_workflow(self):
        """Test complete workflow for choosing gaming activity."""
        # Get tools
        weather_tool = next(tool for tool in self.tools if tool.name == "check_weather")
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        state_tool = next(tool for tool in self.tools if tool.name == "check_state")
        
        # Step 1: Check weather
        weather_result = weather_tool._run("")
        self.assertIn("Weather check complete", weather_result)
        
        # Step 2: Try to play games without equipment (should fail)
        gaming_result = activity_tool._run('{"activity": "Play games"}')
        self.assertIn("Rule violation", gaming_result)
        self.assertIn("Missing required items", gaming_result)
        
        # Step 3: Buy required equipment
        tv_result = shopping_tool._run('{"item": "TV"}')
        self.assertIn("Successfully purchased", tv_result)
        
        xbox_result = shopping_tool._run('{"item": "Xbox"}')
        self.assertIn("Successfully purchased", xbox_result)
        
        # Step 4: Check state to verify inventory
        state_result = state_tool._run("")
        self.assertIn("TV", state_result)
        self.assertIn("Xbox", state_result)
        
        # Step 5: Now try to play games (should succeed)
        gaming_result = activity_tool._run('{"activity": "Play games"}')
        self.assertIn("Activity chosen", gaming_result)
        self.assertIn("Play games", gaming_result)
        
        # Verify final state
        self.assertEqual(self.state.chosen_activity.value, "Play games")
        self.assertIn("TV", self.state.inventory)
        self.assertIn("Xbox", self.state.inventory)
    
    def test_complete_camping_workflow(self):
        """Test complete workflow for choosing camping activity."""
        weather_tool = next(tool for tool in self.tools if tool.name == "check_weather")
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        # Step 1: Check weather (force it to be sunny for camping)
        weather_result = weather_tool._run("")
        self.assertIn("Weather check complete", weather_result)
        
        # Force sunny weather for camping test
        from policy_enforcer.state import WeatherCondition
        self.state.set_weather(WeatherCondition.SUNNY)
        
        # Step 2: Buy hiking boots
        boots_result = shopping_tool._run('{"item": "Hiking Boots"}')
        self.assertIn("Successfully purchased", boots_result)
        
        # Step 3: Choose camping activity
        camping_result = activity_tool._run('{"activity": "Go Camping"}')
        self.assertIn("Activity chosen", camping_result)
        
        # Verify state
        self.assertIsNotNone(self.state.chosen_activity)
        self.assertEqual(self.state.chosen_activity.value, "Go Camping")
        self.assertIn("Hiking Boots", self.state.inventory)
    
    def test_weather_prevents_camping(self):
        """Test that rainy weather prevents camping."""
        # Manually set rainy weather
        from policy_enforcer.state import WeatherCondition
        self.state.set_weather(WeatherCondition.RAINING)
        
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        # Buy required equipment
        shopping_tool._run('{"item": "Hiking Boots"}')
        
        # Try camping in rain (should fail)
        camping_result = activity_tool._run('{"activity": "Go Camping"}')
        self.assertIn("Rule violation", camping_result)
        self.assertIn("raining", camping_result)
    
    def test_weather_check_rule_enforcement(self):
        """Test that weather can only be checked once."""
        weather_tool = next(tool for tool in self.tools if tool.name == "check_weather")
        
        # First check should succeed
        first_result = weather_tool._run("")
        self.assertIn("Weather check complete", first_result)
        
        # Second check should fail
        second_result = weather_tool._run("")
        self.assertIn("Weather has already been checked", second_result)
    
    def test_langchain_json_input_compatibility(self):
        """Test compatibility with LangChain JSON string inputs."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        # Test various JSON string formats
        json_inputs = [
            '{"item": "TV"}',
            '{"item": "Xbox"}',
            '{"activity": "Play games"}'
        ]
        
        # Shopping with JSON strings
        tv_result = shopping_tool._run(json_inputs[0])
        self.assertIn("Successfully purchased", tv_result)
        
        xbox_result = shopping_tool._run(json_inputs[1])
        self.assertIn("Successfully purchased", xbox_result)
        
        # Set up weather for activity
        weather_tool = next(tool for tool in self.tools if tool.name == "check_weather")
        weather_tool._run("")
        
        # Activity with JSON string
        activity_result = activity_tool._run(json_inputs[2])
        self.assertIn("Activity chosen", activity_result)
    
    def test_state_persistence_across_tool_calls(self):
        """Test that state persists correctly across multiple tool calls."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        state_tool = next(tool for tool in self.tools if tool.name == "check_state")
        
        # Initial state should be empty
        initial_state = state_tool._run("")
        self.assertIn("Inventory: Empty", initial_state)
        
        # Buy first item
        shopping_tool._run('{"item": "TV"}')
        state_after_first = state_tool._run("")
        self.assertIn("TV", state_after_first)
        self.assertNotIn("Xbox", state_after_first)
        
        # Buy second item
        shopping_tool._run('{"item": "Xbox"}')
        state_after_second = state_tool._run("")
        self.assertIn("TV", state_after_second)
        self.assertIn("Xbox", state_after_second)
        
        # Verify inventory count
        self.assertEqual(len(self.state.inventory), 2)
    
    def test_rule_engine_integration(self):
        """Test rule engine integration with tools."""
        # Test that rules are properly enforced through tools
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        # Try each activity without proper setup
        activities = ["Play games", "Go Camping", "Swimming"]
        
        for activity in activities:
            result = activity_tool._run(f'{{"activity": "{activity}"}}')
            # All should fail due to missing equipment or unknown weather
            self.assertIn("Rule violation", result)
    
    def test_enhanced_state_reporting(self):
        """Test enhanced state reporting in tool outputs."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        weather_tool = next(tool for tool in self.tools if tool.name == "check_weather")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        # Shopping should report current inventory
        result = shopping_tool._run('{"item": "TV"}')
        self.assertIn("📊 Current inventory:", result)
        
        # Weather should report status
        result = weather_tool._run("")
        self.assertIn("📊 Weather status:", result)
        
        # Set up for activity
        shopping_tool._run('{"item": "Xbox"}')
        
        # Activity should report state information
        result = activity_tool._run('{"activity": "Play games"}')
        self.assertIn("📊 Current activity:", result)
        self.assertIn("📊 Current inventory:", result)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the system."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_state()
        self.tools = get_tools()
    
    def test_invalid_item_handling(self):
        """Test handling of invalid items."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        
        result = shopping_tool._run('{"item": "NonexistentItem"}')
        self.assertIn("Invalid item", result)
        self.assertIn("Available items:", result)
    
    def test_invalid_activity_handling(self):
        """Test handling of invalid activities."""
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        result = activity_tool._run('{"activity": "InvalidActivity"}')
        self.assertIn("Invalid activity", result)
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON inputs."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        
        # Should treat malformed JSON as plain string
        result = shopping_tool._run('{"item": TV}')  # Missing quotes
        self.assertIn("Invalid item", result)  # Because it treats whole string as item name
    
    def test_empty_input_handling(self):
        """Test handling of empty inputs."""
        shopping_tool = next(tool for tool in self.tools if tool.name == "shopping")
        activity_tool = next(tool for tool in self.tools if tool.name == "choose_activity")
        
        shopping_result = shopping_tool._run("")
        self.assertIn("No item specified", shopping_result)
        
        activity_result = activity_tool._run("")
        self.assertIn("No activity specified", activity_result)


if __name__ == '__main__':
    unittest.main()
