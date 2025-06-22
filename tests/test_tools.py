"""
Unit tests for the tools module.
"""

import unittest
from unittest.mock import patch, MagicMock
from policy_enforcer.tools import (
    validate_item_input, parse_langchain_input,
    CheckWeatherTool, ShoppingTool, ChooseActivityTool, CheckStateTool,
    get_tools
)
from policy_enforcer.state import AgentState, WeatherCondition, Activity, reset_state


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""
    
    def test_validate_item_input_valid(self):
        """Test validating valid items."""
        self.assertIsNone(validate_item_input("TV"))
        self.assertIsNone(validate_item_input("Xbox"))
        self.assertIsNone(validate_item_input("Hiking Boots"))
        self.assertIsNone(validate_item_input("Goggles"))
        self.assertIsNone(validate_item_input("Sunscreen"))
    
    def test_validate_item_input_invalid(self):
        """Test validating invalid items."""
        result = validate_item_input("Invalid Item")
        self.assertIsNotNone(result)
        self.assertIn("Invalid item", result)
        self.assertIn("Available items:", result)
    
    def test_parse_langchain_input_dict(self):
        """Test parsing dictionary input."""
        input_dict = {"item": "TV"}
        result = parse_langchain_input(input_dict, "item")
        self.assertEqual(result, input_dict)
    
    def test_parse_langchain_input_json_string(self):
        """Test parsing JSON string input."""
        json_string = '{"item": "TV"}'
        result = parse_langchain_input(json_string, "item")
        self.assertEqual(result, {"item": "TV"})
    
    def test_parse_langchain_input_plain_string(self):
        """Test parsing plain string input."""
        plain_string = "TV"
        result = parse_langchain_input(plain_string, "item")
        self.assertEqual(result, {"item": "TV"})
    
    def test_parse_langchain_input_invalid_json(self):
        """Test parsing invalid JSON string."""
        invalid_json = '{"item": TV}'  # Missing quotes
        result = parse_langchain_input(invalid_json, "item")
        self.assertEqual(result, {"item": invalid_json})
    
    def test_parse_langchain_input_other_types(self):
        """Test parsing other input types."""
        result = parse_langchain_input(None, "item")
        self.assertEqual(result, {})
        
        result = parse_langchain_input(123, "item")
        self.assertEqual(result, {})


class TestCheckWeatherTool(unittest.TestCase):
    """Test the CheckWeatherTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CheckWeatherTool()
        reset_state()
    
    def test_tool_properties(self):
        """Test tool properties."""
        self.assertEqual(self.tool.name, "check_weather")
        self.assertIn("weather", self.tool.description.lower())
    
    def test_parse_input(self):
        """Test input parsing."""
        result = self.tool.parse_input("anything")
        self.assertEqual(result, {})
    
    @patch('policy_enforcer.tools.random.choice')
    def test_execute_first_time(self, mock_choice):
        """Test executing weather check first time."""
        mock_choice.return_value = WeatherCondition.SUNNY
        
        result = self.tool.execute()
        self.assertIn("Weather check complete", result)
        self.assertIn("sunny", result)
        self.assertIn("Known and checked", result)
        
        # Verify state was updated
        from policy_enforcer.state import get_state
        state = get_state()
        self.assertEqual(state.weather, WeatherCondition.SUNNY)
        self.assertTrue(state.weather_checked)
    
    def test_execute_already_checked(self):
        """Test executing weather check when already checked."""
        from policy_enforcer.state import get_state
        state = get_state()
        state.set_weather(WeatherCondition.RAINING)
        
        result = self.tool.execute()
        self.assertIn("already checked", result)
        self.assertIn("raining", result)
    
    def test_run_integration(self):
        """Test full _run method integration."""
        result = self.tool._run("")
        self.assertIn("Weather check complete", result)


class TestShoppingTool(unittest.TestCase):
    """Test the ShoppingTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ShoppingTool()
        reset_state()
    
    def test_tool_properties(self):
        """Test tool properties."""
        self.assertEqual(self.tool.name, "shopping")
        self.assertIn("Purchase", self.tool.description)
    
    def test_parse_input_json_string(self):
        """Test parsing JSON string input."""
        result = self.tool.parse_input('{"item": "TV"}')
        self.assertEqual(result, {"item": "TV"})
    
    def test_parse_input_plain_string(self):
        """Test parsing plain string input."""
        result = self.tool.parse_input("Xbox")
        self.assertEqual(result, {"item": "Xbox"})
    
    def test_execute_valid_item(self):
        """Test executing with valid item."""
        result = self.tool.execute(item="TV")
        self.assertIn("Successfully purchased", result)
        self.assertIn("TV", result)
        self.assertIn("Current inventory: TV", result)
        
        # Verify state was updated
        from policy_enforcer.state import get_state
        state = get_state()
        self.assertIn("TV", state.inventory)
    
    def test_execute_invalid_item(self):
        """Test executing with invalid item."""
        result = self.tool.execute(item="Invalid Item")
        self.assertIn("Invalid item", result)
        self.assertIn("Available items:", result)
    
    def test_execute_no_item(self):
        """Test executing without item."""
        result = self.tool.execute()
        self.assertIn("No item specified", result)
    
    def test_run_integration_json(self):
        """Test full _run method with JSON input."""
        result = self.tool._run('{"item": "Xbox"}')
        self.assertIn("Successfully purchased", result)
        self.assertIn("Xbox", result)
    
    def test_multiple_purchases(self):
        """Test multiple purchases update inventory correctly."""
        self.tool.execute(item="TV")
        result = self.tool.execute(item="Xbox")
        
        self.assertIn("Current inventory:", result)
        # Should show both items (order may vary)
        self.assertTrue("TV" in result and "Xbox" in result)


class TestChooseActivityTool(unittest.TestCase):
    """Test the ChooseActivityTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ChooseActivityTool()
        reset_state()
    
    def test_tool_properties(self):
        """Test tool properties."""
        self.assertEqual(self.tool.name, "choose_activity")
        self.assertIn("Choose an activity", self.tool.description)
    
    def test_parse_input_json_string(self):
        """Test parsing JSON string input."""
        result = self.tool.parse_input('{"activity": "Play games"}')
        self.assertEqual(result, {"activity": "Play games"})
    
    def test_execute_valid_activity_with_equipment(self):
        """Test executing valid activity with required equipment."""
        # Set up state to allow gaming
        from policy_enforcer.state import get_state
        state = get_state()
        state.add_to_inventory("TV")
        state.add_to_inventory("Xbox")
        state.set_weather(WeatherCondition.SUNNY)
        
        result = self.tool.execute(activity="Play games")
        self.assertIn("Activity chosen", result)
        self.assertIn("Play games", result)
        self.assertIn("Current inventory:", result)
        
        # Verify state was updated
        self.assertEqual(state.chosen_activity, Activity.PLAY_GAMES)
    
    def test_execute_invalid_activity(self):
        """Test executing with invalid activity."""
        result = self.tool.execute(activity="Invalid Activity")
        self.assertIn("Invalid activity", result)
    
    def test_execute_no_activity(self):
        """Test executing without activity."""
        result = self.tool.execute()
        self.assertIn("No activity specified", result)
    
    def test_check_tool_rules_with_activity(self):
        """Test rule checking with activity."""
        # Should fail without equipment
        rule_violation = self.tool.check_tool_rules(activity="Play games")
        self.assertIsNotNone(rule_violation)
        self.assertIn("Missing required items", rule_violation)
    
    def test_run_integration_rule_violation(self):
        """Test full _run method with rule violation."""
        result = self.tool._run('{"activity": "Play games"}')
        self.assertIn("Rule violation", result)
        self.assertIn("Missing required items", result)


class TestCheckStateTool(unittest.TestCase):
    """Test the CheckStateTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CheckStateTool()
        reset_state()
    
    def test_tool_properties(self):
        """Test tool properties."""
        self.assertEqual(self.tool.name, "check_state")
        self.assertIn("current state", self.tool.description.lower())
    
    def test_execute_empty_state(self):
        """Test executing with empty state."""
        result = self.tool.execute()
        self.assertIn("Current Agent State", result)
        self.assertIn("Inventory: Empty", result)
        self.assertIn("Weather: unknown", result)
        self.assertIn("Current Activity: None chosen", result)
    
    def test_execute_populated_state(self):
        """Test executing with populated state."""
        from policy_enforcer.state import get_state
        state = get_state()
        state.add_to_inventory("TV")
        state.add_to_inventory("Xbox")
        state.set_weather(WeatherCondition.SUNNY)
        state.set_activity(Activity.PLAY_GAMES)
        
        result = self.tool.execute()
        self.assertIn("TV", result)
        self.assertIn("Xbox", result)
        self.assertIn("sunny", result)
        self.assertIn("Play games", result)
    
    def test_run_integration(self):
        """Test full _run method integration."""
        result = self.tool._run("")
        self.assertIn("Current Agent State", result)


class TestGetTools(unittest.TestCase):
    """Test the get_tools function."""
    
    def test_get_tools_count(self):
        """Test that get_tools returns correct number of tools."""
        tools = get_tools()
        self.assertEqual(len(tools), 4)
    
    def test_get_tools_types(self):
        """Test that get_tools returns correct tool types."""
        tools = get_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_names = ["check_weather", "shopping", "choose_activity", "check_state"]
        self.assertEqual(sorted(tool_names), sorted(expected_names))
    
    def test_get_tools_instances(self):
        """Test that get_tools returns proper tool instances."""
        tools = get_tools()
        
        weather_tool = next(tool for tool in tools if tool.name == "check_weather")
        self.assertIsInstance(weather_tool, CheckWeatherTool)
        
        shopping_tool = next(tool for tool in tools if tool.name == "shopping")
        self.assertIsInstance(shopping_tool, ShoppingTool)
        
        activity_tool = next(tool for tool in tools if tool.name == "choose_activity")
        self.assertIsInstance(activity_tool, ChooseActivityTool)
        
        state_tool = next(tool for tool in tools if tool.name == "check_state")
        self.assertIsInstance(state_tool, CheckStateTool)


if __name__ == '__main__':
    unittest.main()
