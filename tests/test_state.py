"""
Unit tests for the state module.
"""

import unittest
from policy_enforcer.state import AgentState, WeatherCondition, Activity, get_state, reset_state


class TestWeatherCondition(unittest.TestCase):
    """Test the WeatherCondition enum."""
    
    def test_weather_values(self):
        """Test weather condition values."""
        self.assertEqual(WeatherCondition.SUNNY.value, "sunny")
        self.assertEqual(WeatherCondition.RAINING.value, "raining")
        self.assertEqual(WeatherCondition.SNOWING.value, "snowing")
        self.assertEqual(WeatherCondition.UNKNOWN.value, "unknown")


class TestActivity(unittest.TestCase):
    """Test the Activity enum."""
    
    def test_activity_values(self):
        """Test activity values."""
        self.assertEqual(Activity.PLAY_GAMES.value, "Play games")
        self.assertEqual(Activity.GO_CAMPING.value, "Go Camping")
        self.assertEqual(Activity.SWIMMING.value, "Swimming")


class TestAgentState(unittest.TestCase):
    """Test the AgentState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = AgentState()
    
    def test_initial_state(self):
        """Test initial state values."""
        self.assertEqual(self.state.inventory, set())
        self.assertEqual(self.state.weather, WeatherCondition.UNKNOWN)
        self.assertFalse(self.state.weather_checked)
        self.assertIsNone(self.state.chosen_activity)
        self.assertEqual(self.state.shopping_history, [])
    
    def test_add_to_inventory(self):
        """Test adding items to inventory."""
        self.state.add_to_inventory("TV")
        self.assertIn("TV", self.state.inventory)
        self.assertIn("TV", self.state.shopping_history)
        
        self.state.add_to_inventory("Xbox")
        self.assertIn("Xbox", self.state.inventory)
        self.assertEqual(len(self.state.inventory), 2)
        self.assertEqual(self.state.shopping_history, ["TV", "Xbox"])
    
    def test_add_duplicate_to_inventory(self):
        """Test adding duplicate items to inventory."""
        self.state.add_to_inventory("TV")
        self.state.add_to_inventory("TV")  # Duplicate
        
        # Set should only contain one TV
        self.assertEqual(len(self.state.inventory), 1)
        self.assertIn("TV", self.state.inventory)
        
        # But history should show both purchases
        self.assertEqual(self.state.shopping_history, ["TV", "TV"])
    
    def test_has_item(self):
        """Test checking if user has an item."""
        self.assertFalse(self.state.has_item("TV"))
        
        self.state.add_to_inventory("TV")
        self.assertTrue(self.state.has_item("TV"))
        self.assertFalse(self.state.has_item("Xbox"))
    
    def test_has_items(self):
        """Test checking if user has multiple items."""
        items = ["TV", "Xbox"]
        self.assertFalse(self.state.has_items(items))
        
        self.state.add_to_inventory("TV")
        self.assertFalse(self.state.has_items(items))
        
        self.state.add_to_inventory("Xbox")
        self.assertTrue(self.state.has_items(items))
    
    def test_set_weather(self):
        """Test setting weather condition."""
        self.state.set_weather(WeatherCondition.SUNNY)
        self.assertEqual(self.state.weather, WeatherCondition.SUNNY)
        self.assertTrue(self.state.weather_checked)
        
        self.state.set_weather(WeatherCondition.RAINING)
        self.assertEqual(self.state.weather, WeatherCondition.RAINING)
        self.assertTrue(self.state.weather_checked)
    
    def test_set_activity(self):
        """Test setting chosen activity."""
        self.state.set_activity(Activity.PLAY_GAMES)
        self.assertEqual(self.state.chosen_activity, Activity.PLAY_GAMES)
        
        self.state.set_activity(Activity.SWIMMING)
        self.assertEqual(self.state.chosen_activity, Activity.SWIMMING)
    
    def test_to_dict(self):
        """Test converting state to dictionary."""
        self.state.add_to_inventory("TV")
        self.state.set_weather(WeatherCondition.SUNNY)
        self.state.set_activity(Activity.PLAY_GAMES)
        
        state_dict = self.state.to_dict()
        expected = {
            "inventory": ["TV"],
            "weather": "sunny",
            "weather_checked": True,
            "chosen_activity": "Play games",
            "shopping_history": ["TV"]
        }
        
        self.assertEqual(state_dict["weather"], expected["weather"])
        self.assertEqual(state_dict["weather_checked"], expected["weather_checked"])
        self.assertEqual(state_dict["chosen_activity"], expected["chosen_activity"])
        self.assertEqual(state_dict["shopping_history"], expected["shopping_history"])
        self.assertEqual(sorted(state_dict["inventory"]), sorted(expected["inventory"]))
    
    def test_get_summary(self):
        """Test getting state summary."""
        summary = self.state.get_summary()
        self.assertIn("Inventory: Empty", summary)
        self.assertIn("Weather: unknown", summary)
        self.assertIn("Weather checked: False", summary)
        
        self.state.add_to_inventory("TV")
        self.state.add_to_inventory("Xbox")
        self.state.set_weather(WeatherCondition.SUNNY)
        self.state.set_activity(Activity.PLAY_GAMES)
        
        summary = self.state.get_summary()
        self.assertIn("TV", summary)
        self.assertIn("Xbox", summary)
        self.assertIn("Weather: sunny", summary)
        self.assertIn("Weather checked: True", summary)
        self.assertIn("Chosen activity: Play games", summary)


class TestGlobalState(unittest.TestCase):
    """Test global state management functions."""
    
    def setUp(self):
        """Reset state before each test."""
        reset_state()
    
    def test_get_state(self):
        """Test getting global state."""
        state = get_state()
        self.assertIsInstance(state, AgentState)
        self.assertEqual(state.inventory, set())
    
    def test_reset_state(self):
        """Test resetting global state."""
        state = get_state()
        state.add_to_inventory("TV")
        state.set_weather(WeatherCondition.SUNNY)
        
        # Verify state is modified
        self.assertIn("TV", state.inventory)
        self.assertEqual(state.weather, WeatherCondition.SUNNY)
        
        # Reset and verify it's clean
        reset_state()
        new_state = get_state()
        self.assertEqual(new_state.inventory, set())
        self.assertEqual(new_state.weather, WeatherCondition.UNKNOWN)
        self.assertFalse(new_state.weather_checked)
    
    def test_state_persistence(self):
        """Test that state persists across get_state calls."""
        state1 = get_state()
        state1.add_to_inventory("TV")
        
        state2 = get_state()
        self.assertIn("TV", state2.inventory)
        self.assertIs(state1, state2)  # Should be the same object


if __name__ == '__main__':
    unittest.main()
