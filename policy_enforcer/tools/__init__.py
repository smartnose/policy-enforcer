"""
Tools for the policy enforcer agent.
"""

import random
from typing import Any, Dict, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..state import get_state, WeatherCondition, Activity
from ..rules import get_rule_engine, RuleResult


class WeatherToolInput(BaseModel):
    """Input for the weather tool."""
    pass  # No input required


class ShoppingToolInput(BaseModel):
    """Input for the shopping tool."""
    item: str = Field(description="The item to purchase")


class ActivityToolInput(BaseModel):
    """Input for the activity tool."""
    activity: str = Field(description="The activity to choose: 'Play games', 'Go Camping', or 'Swimming'")


class PolicyEnforcedTool(BaseTool):
    """Base class for tools with policy enforcement."""
    
    def check_rules(self, **kwargs) -> Optional[str]:
        """Check business rules before executing the tool. Return error message if rules violated."""
        state = get_state()
        rule_engine = get_rule_engine()
        
        # Check tool-specific rules
        result = rule_engine.check_tool_rules(state, self.name)
        if not result.allowed:
            return result.reason
        
        return None
    
    def _run(self, **kwargs) -> str:
        # Check rules first
        rule_violation = self.check_rules(**kwargs)
        if rule_violation:
            return f"❌ Rule violation: {rule_violation}"
        
        # Execute the actual tool logic
        return self.execute(**kwargs)
    
    def execute(self, **kwargs) -> str:
        """Override this method to implement tool-specific logic."""
        raise NotImplementedError


class CheckWeatherTool(PolicyEnforcedTool):
    """Tool to check the weather condition."""
    
    name: str = "check_weather"
    description: str = "Check the current weather condition. Returns a random weather condition."
    args_schema: Type[BaseModel] = WeatherToolInput
    
    def execute(self, **kwargs) -> str:
        state = get_state()
        
        # Generate random weather
        weather_options = [WeatherCondition.SUNNY, WeatherCondition.RAINING, WeatherCondition.SNOWING]
        new_weather = random.choice(weather_options)
        
        # Update state
        state.set_weather(new_weather)
        
        return f"🌤️ Weather check complete! Current weather: {new_weather.value}"


class ShoppingTool(PolicyEnforcedTool):
    """Tool to purchase items."""
    
    name: str = "shopping"
    description: str = "Purchase an item and add it to your inventory. Specify the item name."
    args_schema: Type[BaseModel] = ShoppingToolInput
    
    def execute(self, item: str, **kwargs) -> str:
        state = get_state()
        
        # Add item to inventory
        state.add_to_inventory(item)
        
        return f"🛒 Successfully purchased: {item}. Added to inventory!"


class ChooseActivityTool(PolicyEnforcedTool):
    """Tool to choose an activity."""
    
    name: str = "choose_activity"
    description: str = """Choose an activity from: 'Play games', 'Go Camping', or 'Swimming'. 
    The choice will be validated against business rules."""
    args_schema: Type[BaseModel] = ActivityToolInput
    
    def check_rules(self, activity: str, **kwargs) -> Optional[str]:
        """Check activity-specific rules in addition to tool rules."""
        # First check general tool rules
        rule_violation = super().check_rules(**kwargs)
        if rule_violation:
            return rule_violation
        
        # Then check activity-specific rules
        state = get_state()
        rule_engine = get_rule_engine()
        
        result = rule_engine.check_activity_rules(state, activity)
        if not result.allowed:
            return result.reason
        
        return None
    
    def execute(self, activity: str, **kwargs) -> str:
        state = get_state()
        
        # Validate activity choice
        valid_activities = [a.value for a in Activity]
        if activity not in valid_activities:
            return f"❌ Invalid activity. Choose from: {', '.join(valid_activities)}"
        
        # Set the chosen activity
        activity_enum = Activity(activity)
        state.set_activity(activity_enum)
        
        return f"🎯 Activity chosen: {activity}! Have fun!"


def get_tools() -> list[BaseTool]:
    """Get all available tools."""
    return [
        CheckWeatherTool(),
        ShoppingTool(),
        ChooseActivityTool()
    ]
