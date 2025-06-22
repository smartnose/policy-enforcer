"""
Tools for the policy enforcer agent.
"""

import random
from typing import Any, Dict, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..state import get_state, WeatherCondition, Activity
from ..rules import get_rule_engine, RuleResult
from ..items import Item, ItemRequirements


class WeatherToolInput(BaseModel):
    """Input for the weather tool."""
    pass  # No input required


class ShoppingToolInput(BaseModel):
    """Input for the shopping tool."""
    item: str = Field(description="The item to purchase: TV, Xbox, Hiking Boots, Goggles, or Sunscreen")


class ActivityToolInput(BaseModel):
    """Input for the activity tool."""
    activity: str = Field(description="The activity to choose: 'Play games', 'Go Camping', or 'Swimming'")


class StateToolInput(BaseModel):
    """Input for the state checking tool."""
    pass  # No input required


def validate_item_input(item: str) -> Optional[str]:
    """Validate item input and return error message if invalid."""
    if not ItemRequirements.is_valid_item(item):
        available_items = ", ".join(ItemRequirements.get_all_items())
        return f"Invalid item '{item}'. Available items: {available_items}"
    return None


def parse_langchain_input(tool_input: Any, key: str) -> Dict[str, Any]:
    """
    Parse LangChain tool input handling the JSON string issue.
    
    This is a workaround for LangChain parameter mapping issue where
    LangChain passes JSON strings like '{"key": "value"}' instead of 
    parsed dictionaries.
    
    Args:
        tool_input: The input from LangChain (dict, JSON string, or plain string)
        key: The expected parameter key name
    
    Returns:
        Dictionary with parsed parameters
    """
    if isinstance(tool_input, dict):
        return tool_input
    elif isinstance(tool_input, str):
        # Handle case where LangChain passes JSON string instead of parsed dict
        import json
        try:
            parsed = json.loads(tool_input)
            if isinstance(parsed, dict):
                return parsed
            else:
                return {key: tool_input}
        except (json.JSONDecodeError, TypeError):
            # If not JSON, treat as plain string value
            return {key: tool_input}
    else:
        return {}


class PolicyEnforcedTool(BaseTool):
    """Base class for tools with policy enforcement."""
    
    def check_tool_rules(self, **kwargs) -> Optional[str]:
        """Check tool-specific business rules. Override in subclasses for custom rule checking."""
        state = get_state()
        rule_engine = get_rule_engine()
        
        # Check general tool-specific rules
        result = rule_engine.check_tool_rules(state, tool_name=self.name)
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
            # Simple fallback - let subclasses handle specific parsing
            return {"input": tool_input}
        else:
            return {}
    
    def _run(self, tool_input: Optional[str] = None, **kwargs) -> str:
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

        if( state.weather_checked and state.weather != WeatherCondition.UNKNOWN):
            return (f"🌤️ Weather already checked! Current weather: {state.weather.value}\n"
                    f"📊 Weather status: Known and checked")
        
        new_weather = random.choice(weather_options)
        
        # Update state
        state.set_weather(new_weather)
        
        return (f"🌤️ Weather check complete! Current weather: {new_weather.value}\n"
                f"📊 Weather status: Known and checked")


class ShoppingTool(PolicyEnforcedTool):
    """Tool to purchase items."""
    
    name: str = "shopping"
    description: str = "Purchase an item and add it to your inventory. Available items: TV, Xbox, Hiking Boots, Goggles, Sunscreen"
    args_schema: Type[BaseModel] = ShoppingToolInput
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Parse shopping tool input to extract item parameter."""
        return parse_langchain_input(tool_input, "item")
    
    def execute(self, *, item: Optional[str] = None, **kwargs) -> str:
        if not item:
            return "❌ No item specified for purchase."
        
        # Validate the item first
        validation_error = validate_item_input(item)
        if validation_error:
            return f"❌ {validation_error}"
        
        state = get_state()
        
        # Add item to inventory
        state.add_to_inventory(item)
        
        # Enhanced output with state information
        return (f"🛒 Successfully purchased: {item}. Added to inventory!\n"
                f"📊 Current inventory: {', '.join(sorted(state.inventory)) if state.inventory else 'Empty'}")


class ChooseActivityTool(PolicyEnforcedTool):
    """Tool to choose an activity."""
    
    name: str = "choose_activity"
    description: str = """Choose an activity from: 'Play games', 'Go Camping', or 'Swimming'. 
    The choice will be validated against business rules."""
    args_schema: Type[BaseModel] = ActivityToolInput
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """Parse activity tool input to extract activity parameter."""
        return parse_langchain_input(tool_input, "activity")
    
    def _run(self, tool_input: Optional[str] = None, **kwargs) -> str:
        """Custom _run method to validate activity before checking rules."""
        # Parse input into parameters
        params = self.parse_input(tool_input)
        
        # Validate activity format FIRST, before rule checking
        activity = params.get("activity")
        if not activity:
            return "❌ No activity specified."
        
        valid_activities = [a.value for a in Activity]
        if activity not in valid_activities:
            return f"❌ Invalid activity. Choose from: {', '.join(valid_activities)}"
        
        # Now check rules with the validated activity
        rule_violation = self.check_tool_rules(**params)
        if rule_violation:
            return f"❌ Rule violation: {rule_violation}"
        
        # Execute the actual tool logic
        return self.execute(**params)
    
    def check_tool_rules(self, *, activity: Optional[str] = None, **kwargs) -> Optional[str]:
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
    
    def execute(self, *, activity: Optional[str] = None, **kwargs) -> str:
        if not activity:
            return "❌ No activity specified."
        
        state = get_state()
        
        # Validate activity format
        valid_activities = [a.value for a in Activity]
        if activity not in valid_activities:
            return f"❌ Invalid activity. Choose from: {', '.join(valid_activities)}"
        
        # Set the chosen activity (validation already done)
        activity_enum = Activity(activity)
        state.set_activity(activity_enum)
        
        return (f"🎯 Activity chosen: {activity}! Have fun!\n"
                f"📊 Current activity: {activity}\n"
                f"📊 Current inventory: {', '.join(sorted(state.inventory)) if state.inventory else 'Empty'}")


class CheckStateTool(PolicyEnforcedTool):
    """Tool to check the current agent state."""
    
    name: str = "check_state"
    description: str = "Check the current state including inventory, weather, and chosen activity."
    args_schema: Type[BaseModel] = StateToolInput
    
    def parse_input(self, tool_input: Any) -> Dict[str, Any]:
        """State tool doesn't need any input parameters."""
        return {}
    
    def execute(self, **kwargs) -> str:
        state = get_state()
        
        return (f"📊 **Current Agent State:**\n"
                f"🎒 Inventory: {', '.join(sorted(state.inventory)) if state.inventory else 'Empty'}\n"
                f"🌤️ Weather: {state.weather.value} ({'Known' if state.weather_checked else 'Unknown'})\n"
                f"🎯 Current Activity: {state.chosen_activity.value if state.chosen_activity else 'None chosen'}")


def get_tools() -> list[BaseTool]:
    """Get all available tools."""
    return [
        CheckWeatherTool(),
        ShoppingTool(),
        ChooseActivityTool(),
        CheckStateTool()
    ]
