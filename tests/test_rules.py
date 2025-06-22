"""
Unit tests for the rules module.
"""

import unittest
from policy_enforcer.rules import (
    RuleResult, BusinessRule, PlayGamesRule, CampingEquipmentRule,
    SwimmingEquipmentRule, CampingWeatherRule, SwimmingWeatherRule,
    UnknownWeatherRule, WeatherCheckRule, RuleEngine, get_rule_engine
)
from policy_enforcer.state import AgentState, WeatherCondition, Activity
from policy_enforcer.items import Item


class TestRuleResult(unittest.TestCase):
    """Test the RuleResult class."""
    
    def test_allowed_result(self):
        """Test creating allowed result."""
        result = RuleResult(allowed=True)
        self.assertTrue(result.allowed)
        self.assertIsNone(result.reason)
    
    def test_denied_result(self):
        """Test creating denied result."""
        reason = "Test reason"
        result = RuleResult(allowed=False, reason=reason)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, reason)


class TestPlayGamesRule(unittest.TestCase):
    """Test the PlayGamesRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = PlayGamesRule()
        self.state = AgentState()
    
    def test_rule_properties(self):
        """Test rule name and description."""
        self.assertEqual(self.rule.name, "Play Games Equipment Rule")
        self.assertIn("TV", self.rule.description)
        self.assertIn("Xbox", self.rule.description)
    
    def test_check_non_gaming_activity(self):
        """Test rule allows non-gaming activities."""
        result = self.rule.check(self.state, activity="Swimming")
        self.assertTrue(result.allowed)
        
        result = self.rule.check(self.state, activity="Go Camping")
        self.assertTrue(result.allowed)
    
    def test_check_gaming_without_equipment(self):
        """Test rule denies gaming without equipment."""
        result = self.rule.check(self.state, activity="Play games")
        self.assertFalse(result.allowed)
        self.assertIn("Missing required items", result.reason)
        self.assertIn("TV", result.reason)
        self.assertIn("Xbox", result.reason)
    
    def test_check_gaming_with_partial_equipment(self):
        """Test rule denies gaming with partial equipment."""
        self.state.add_to_inventory("TV")
        result = self.rule.check(self.state, activity="Play games")
        self.assertFalse(result.allowed)
        self.assertIn("Xbox", result.reason)
    
    def test_check_gaming_with_full_equipment(self):
        """Test rule allows gaming with full equipment."""
        self.state.add_to_inventory("TV")
        self.state.add_to_inventory("Xbox")
        result = self.rule.check(self.state, activity="Play games")
        self.assertTrue(result.allowed)


class TestCampingEquipmentRule(unittest.TestCase):
    """Test the CampingEquipmentRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = CampingEquipmentRule()
        self.state = AgentState()
    
    def test_check_non_camping_activity(self):
        """Test rule allows non-camping activities."""
        result = self.rule.check(self.state, activity="Play games")
        self.assertTrue(result.allowed)
    
    def test_check_camping_without_boots(self):
        """Test rule denies camping without hiking boots."""
        result = self.rule.check(self.state, activity="Go Camping")
        self.assertFalse(result.allowed)
        self.assertIn("Hiking Boots", result.reason)
    
    def test_check_camping_with_boots(self):
        """Test rule allows camping with hiking boots."""
        self.state.add_to_inventory("Hiking Boots")
        result = self.rule.check(self.state, activity="Go Camping")
        self.assertTrue(result.allowed)


class TestSwimmingEquipmentRule(unittest.TestCase):
    """Test the SwimmingEquipmentRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = SwimmingEquipmentRule()
        self.state = AgentState()
    
    def test_check_non_swimming_activity(self):
        """Test rule allows non-swimming activities."""
        result = self.rule.check(self.state, activity="Play games")
        self.assertTrue(result.allowed)
    
    def test_check_swimming_without_goggles(self):
        """Test rule denies swimming without goggles."""
        result = self.rule.check(self.state, activity="Swimming")
        self.assertFalse(result.allowed)
        self.assertIn("Goggles", result.reason)
    
    def test_check_swimming_with_goggles(self):
        """Test rule allows swimming with goggles."""
        self.state.add_to_inventory("Goggles")
        result = self.rule.check(self.state, activity="Swimming")
        self.assertTrue(result.allowed)


class TestWeatherRules(unittest.TestCase):
    """Test weather-related rules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.camping_rule = CampingWeatherRule()
        self.swimming_rule = SwimmingWeatherRule()
        self.unknown_rule = UnknownWeatherRule()
        self.state = AgentState()
    
    def test_camping_weather_rule_sunny(self):
        """Test camping allowed in sunny weather."""
        self.state.set_weather(WeatherCondition.SUNNY)
        result = self.camping_rule.check(self.state, activity="Go Camping")
        self.assertTrue(result.allowed)
    
    def test_camping_weather_rule_raining(self):
        """Test camping denied in rain."""
        self.state.set_weather(WeatherCondition.RAINING)
        result = self.camping_rule.check(self.state, activity="Go Camping")
        self.assertFalse(result.allowed)
        self.assertIn("raining", result.reason)
    
    def test_swimming_weather_rule_sunny(self):
        """Test swimming allowed in sunny weather."""
        self.state.set_weather(WeatherCondition.SUNNY)
        result = self.swimming_rule.check(self.state, activity="Swimming")
        self.assertTrue(result.allowed)
    
    def test_swimming_weather_rule_snowing(self):
        """Test swimming denied in snow."""
        self.state.set_weather(WeatherCondition.SNOWING)
        result = self.swimming_rule.check(self.state, activity="Swimming")
        self.assertFalse(result.allowed)
        self.assertIn("snowing", result.reason)
    
    def test_unknown_weather_rule_gaming(self):
        """Test gaming allowed with unknown weather."""
        self.state.weather = WeatherCondition.UNKNOWN
        result = self.unknown_rule.check(self.state, activity="Play games")
        self.assertTrue(result.allowed)
    
    def test_unknown_weather_rule_camping(self):
        """Test camping denied with unknown weather."""
        self.state.weather = WeatherCondition.UNKNOWN
        result = self.unknown_rule.check(self.state, activity="Go Camping")
        self.assertFalse(result.allowed)
        self.assertIn("Weather is unknown", result.reason)


class TestWeatherCheckRule(unittest.TestCase):
    """Test the WeatherCheckRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = WeatherCheckRule()
        self.state = AgentState()
    
    def test_check_non_weather_tool(self):
        """Test rule allows non-weather tools."""
        result = self.rule.check(self.state, tool_name="shopping")
        self.assertTrue(result.allowed)
    
    def test_check_weather_tool_first_time(self):
        """Test weather tool allowed first time."""
        result = self.rule.check(self.state, tool_name="check_weather")
        self.assertTrue(result.allowed)
    
    def test_check_weather_tool_second_time(self):
        """Test weather tool denied second time."""
        self.state.set_weather(WeatherCondition.SUNNY)  # This sets weather_checked=True
        result = self.rule.check(self.state, tool_name="check_weather")
        self.assertFalse(result.allowed)
        self.assertIn("already been checked", result.reason)


class TestRuleEngine(unittest.TestCase):
    """Test the RuleEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()
        self.state = AgentState()
    
    def test_engine_has_all_rules(self):
        """Test that engine contains all expected rules."""
        self.assertEqual(len(self.engine.rules), 7)
        
        rule_types = [type(rule).__name__ for rule in self.engine.rules]
        expected_types = [
            'PlayGamesRule', 'CampingEquipmentRule', 'SwimmingEquipmentRule',
            'CampingWeatherRule', 'SwimmingWeatherRule', 'UnknownWeatherRule',
            'WeatherCheckRule'
        ]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, rule_types)
    
    def test_check_activity_rules_allowed(self):
        """Test activity rules when allowed."""
        # Set up state to allow gaming
        self.state.add_to_inventory("TV")
        self.state.add_to_inventory("Xbox")
        self.state.set_weather(WeatherCondition.SUNNY)
        
        result = self.engine.check_activity_rules(self.state, "Play games")
        self.assertTrue(result.allowed)
    
    def test_check_activity_rules_denied_equipment(self):
        """Test activity rules when denied by equipment."""
        self.state.set_weather(WeatherCondition.SUNNY)
        
        result = self.engine.check_activity_rules(self.state, "Play games")
        self.assertFalse(result.allowed)
        self.assertIn("Missing required items", result.reason)
    
    def test_check_activity_rules_denied_weather(self):
        """Test activity rules when denied by weather."""
        self.state.add_to_inventory("Hiking Boots")
        self.state.set_weather(WeatherCondition.RAINING)
        
        result = self.engine.check_activity_rules(self.state, "Go Camping")
        self.assertFalse(result.allowed)
        self.assertIn("raining", result.reason)
    
    def test_check_tool_rules_allowed(self):
        """Test tool rules when allowed."""
        result = self.engine.check_tool_rules(self.state, "check_weather")
        self.assertTrue(result.allowed)
    
    def test_check_tool_rules_denied(self):
        """Test tool rules when denied."""
        self.state.set_weather(WeatherCondition.SUNNY)
        result = self.engine.check_tool_rules(self.state, "check_weather")
        self.assertFalse(result.allowed)
    
    def test_get_rule_descriptions(self):
        """Test getting rule descriptions."""
        descriptions = self.engine.get_rule_descriptions()
        self.assertEqual(len(descriptions), 7)
        self.assertTrue(all(isinstance(desc, str) for desc in descriptions))
    
    def test_get_rules_summary(self):
        """Test getting rules summary."""
        summary = self.engine.get_rules_summary()
        self.assertIn("Business Rules:", summary)
        self.assertIn("1.", summary)
        self.assertIn("7.", summary)


class TestGlobalRuleEngine(unittest.TestCase):
    """Test global rule engine function."""
    
    def test_get_rule_engine(self):
        """Test getting global rule engine."""
        engine = get_rule_engine()
        self.assertIsInstance(engine, RuleEngine)
        self.assertEqual(len(engine.rules), 7)
    
    def test_rule_engine_singleton(self):
        """Test that rule engine is singleton."""
        engine1 = get_rule_engine()
        engine2 = get_rule_engine()
        self.assertIs(engine1, engine2)


if __name__ == '__main__':
    unittest.main()
