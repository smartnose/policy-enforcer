"""
Tools for the policy enforcer agent.
"""

import random
from typing import Any, Dict, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..state import get_state, WeatherCondition, Activity
from ..rules import get_rule_engine, RuleResult
from ..items import ItemRequirements


class WeatherToolInput(BaseModel):
    """Input for the weather tool."""
    pass  # No input required


class ShoppingToolInput(BaseModel):
    """Input for the shopping tool."""
    item: str = Field(description="The item to purchase")


class ActivityToolInput(BaseModel):
    """Input for the activity tool."""
    activity: str = Field(description="The activity to choose: 'Play games', 'Go Camping', or 'Swimming'")


def validate_item_input(item: str) -> Optional[str]:
    """Validate item input and return error message if invalid."""
    if not ItemRequirements.is_valid_item(item):
        available_items = ", ".join(ItemRequirements.get_all_items())
        return f"Invalid item '{item}'. Available items: {available_items}"
    return None


class PolicyEnforcedTool(BaseTool):
    """Base class for tools with policy enforcement."""
    
    def check_tool_rules(self, **kwargs) -> Optional[str]:
        """Check tool-specific business rules. Override in subclasses for custom rule checking."""
        state = get_state()
        rule_engine = get_rule_engine()
        
        # Check general tool-specific rules
        result = rule_engine.check_tool_rules(state, self.name)
        if not result.allowed:
            return result.reason
        
        return None
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Parse tool input into parameters. Override in subclasses for custom parsing."""
        if tool_input is None:
            return {}
        elif isinstance(tool_input, dict):
            return tool_input
        elif isinstance(tool_input, str):
            # Default: assume single parameter tools use the first field name
            if hasattr(self, 'args_schema') and self.args_schema:
                schema_fields = list(self.args_schema.__fields__.keys())
                if schema_fields:
                    return {schema_fields[0]: tool_input}
            return {"input": tool_input}
        else:
            return {}
    
    def _run(self, tool_input: str=None) -> str:
        """Main execution method that handles rule checking and delegates to execute."""
        # Parse input into parameters
        params = self.parse_input(tool_input)
        
        # Check rules first
        rule_violation = self.check_tool_rules(**params)
        if rule_violation:
            return f"❌ Rule violation: {rule_violation}"
        
        # Execute the actual tool logic
        return self.execute(**params)
    
    def execute(self, **kwargs) -> str:
        """Override this method to implement tool-specific logic."""
        raise NotImplementedError


class CheckWeatherTool(PolicyEnforcedTool):
    """Tool to check the weather condition."""
    
    name: str = "check_weather"
    description: str = "Check the current weather condition. Returns a random weather condition."
    args_schema: Type[BaseModel] = WeatherToolInput
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Weather tool doesn't need any input parameters."""
        return {}
    
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
    
    def __init__(self):
        super().__init__()
        # Update description with available items
        available_items = ", ".join(ItemRequirements.get_all_items())
        self.description = f"Purchase an item and add it to your inventory. Available items: {available_items}"
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Parse shopping tool input to extract item parameter."""
        if isinstance(tool_input, dict):
            return tool_input
        elif isinstance(tool_input, str):
            return {"item": tool_input}
        else:
            return {}
    
    def execute(self, item: str = None, **kwargs) -> str:
        if not item:
            return "❌ No item specified for purchase."
        
        # Validate the item first
        validation_error = validate_item_input(item)
        if validation_error:
            return f"❌ {validation_error}"
        
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
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Parse activity tool input to extract activity parameter."""
        if isinstance(tool_input, dict):
            return tool_input
        elif isinstance(tool_input, str):
            return {"activity": tool_input}
        else:
            return {}
    
    def check_tool_rules(self, activity: str = None, **kwargs) -> Optional[str]:
        """Check activity-specific rules in addition to tool rules."""
        # First check general tool rules
        rule_violation = super().check_tool_rules(**kwargs)
        if rule_violation:
            return rule_violation
        
        # Then check activity-specific rules if activity is provided
        if activity:
            state = get_state()
            rule_engine = get_rule_engine()
            
            result = rule_engine.check_activity_rules(state, activity)
            if not result.allowed:
                return result.reason
        
        return None
    
    def execute(self, activity: str = None, **kwargs) -> str:
        if not activity:
            return "❌ No activity specified."
        
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
