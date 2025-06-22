"""
Business rules engine for policy enforcement.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Any
from pydantic import BaseModel

from ..state import AgentState, Activity, WeatherCondition
from ..items import Item, ItemRequirements


class RuleResult(BaseModel):
    """Result of a business rule evaluation."""
    allowed: bool
    reason: Optional[str] = None


class BusinessRule(ABC):
    """Abstract base class for business rules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def check(self, state: AgentState, **kwargs) -> RuleResult:
        """Check if the rule allows the action.
        
        Args:
            state: Current agent state
            **kwargs: Keyword arguments specific to each rule type
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class PlayGamesRule(BusinessRule):
    """Rule: User must have TV and Xbox to play games."""
    
    def __init__(self):
        super().__init__(
            name="Play Games Equipment Rule",
            description=f"The user must have a {Item.TV.value} and an {Item.XBOX.value} before they can play games"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if activity != Activity.PLAY_GAMES.value:
            return RuleResult(allowed=True)
        
        required_items = ItemRequirements.PLAY_GAMES
        missing_items = ItemRequirements.get_missing_items(activity, state.inventory)
        
        if not missing_items:
            return RuleResult(allowed=True)
        
        missing_names = [item.value for item in missing_items]
        return RuleResult(
            allowed=False,
            reason=f"Cannot play games. Missing required items: {', '.join(missing_names)}"
        )


class CampingEquipmentRule(BusinessRule):
    """Rule: User must have Hiking Boots to go camping."""
    
    def __init__(self):
        super().__init__(
            name="Camping Equipment Rule",
            description=f"The user must have {Item.HIKING_BOOTS.value} before they can go camping"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if activity != Activity.GO_CAMPING.value:
            return RuleResult(allowed=True)
        
        missing_items = ItemRequirements.get_missing_items(activity, state.inventory)
        
        if not missing_items:
            return RuleResult(allowed=True)
        
        return RuleResult(
            allowed=False,
            reason=f"Cannot go camping. Missing required item: {Item.HIKING_BOOTS.value}"
        )


class SwimmingEquipmentRule(BusinessRule):
    """Rule: User must have Goggles to go swimming."""
    
    def __init__(self):
        super().__init__(
            name="Swimming Equipment Rule",
            description=f"The user must have {Item.GOGGLES.value} before they can go swimming"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if activity != Activity.SWIMMING.value:
            return RuleResult(allowed=True)
        
        missing_items = ItemRequirements.get_missing_items(activity, state.inventory)
        
        if not missing_items:
            return RuleResult(allowed=True)
        
        return RuleResult(
            allowed=False,
            reason=f"Cannot go swimming. Missing required item: {Item.GOGGLES.value}"
        )


class CampingWeatherRule(BusinessRule):
    """Rule: Cannot go camping if it's raining."""
    
    def __init__(self):
        super().__init__(
            name="Camping Weather Rule",
            description="If the weather is raining, the user cannot go camping"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if activity != Activity.GO_CAMPING.value:
            return RuleResult(allowed=True)
        
        if state.weather == WeatherCondition.RAINING:
            return RuleResult(
                allowed=False,
                reason="Cannot go camping because it's raining"
            )
        
        return RuleResult(allowed=True)


class SwimmingWeatherRule(BusinessRule):
    """Rule: Cannot go swimming if it's snowing."""
    
    def __init__(self):
        super().__init__(
            name="Swimming Weather Rule",
            description="If the weather is snowing, the user cannot go swimming"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if activity != Activity.SWIMMING.value:
            return RuleResult(allowed=True)
        
        if state.weather == WeatherCondition.SNOWING:
            return RuleResult(
                allowed=False,
                reason="Cannot go swimming because it's snowing"
            )
        
        return RuleResult(allowed=True)


class UnknownWeatherRule(BusinessRule):
    """Rule: If weather is unknown, can only play games."""
    
    def __init__(self):
        super().__init__(
            name="Unknown Weather Rule",
            description="If the weather is unknown, the user can only play games"
        )
    
    def check(self, state: AgentState, *, activity: Optional[str] = None, **kwargs) -> RuleResult:
        if state.weather != WeatherCondition.UNKNOWN:
            return RuleResult(allowed=True)
        
        if activity == Activity.PLAY_GAMES.value:
            return RuleResult(allowed=True)
        
        return RuleResult(
            allowed=False,
            reason="Weather is unknown. You can only play games until weather is checked"
        )


class WeatherCheckRule(BusinessRule):
    """Rule: Weather tool cannot be called again if weather is already known."""
    
    def __init__(self):
        super().__init__(
            name="Weather Check Rule",
            description="If the weather is already known, the weather tool cannot be called again. Do not call weather tool twice."
        )
    
    def check(self, state: AgentState, *, tool_name: Optional[str] = None, **kwargs) -> RuleResult:
        if tool_name != "check_weather":
            return RuleResult(allowed=True)
        
        if state.weather_checked and state.weather != WeatherCondition.UNKNOWN:
            return RuleResult(
                allowed=False,
                reason="Weather has already been checked and is known. Cannot check weather again"
            )
        
        return RuleResult(allowed=True)


class RuleEngine:
    """Engine for evaluating business rules."""
    
    def __init__(self):
        self.rules = [
            PlayGamesRule(),
            CampingEquipmentRule(),
            SwimmingEquipmentRule(),
            CampingWeatherRule(),
            SwimmingWeatherRule(),
            UnknownWeatherRule(),
            WeatherCheckRule()
        ]
    
    def check_activity_rules(self, state: AgentState, activity: str) -> RuleResult:
        """Check all rules related to choosing an activity."""
        for rule in self.rules:
            if isinstance(rule, (PlayGamesRule, CampingEquipmentRule, SwimmingEquipmentRule,
                               CampingWeatherRule, SwimmingWeatherRule, UnknownWeatherRule)):
                result = rule.check(state, activity=activity)
                if not result.allowed:
                    return result
        return RuleResult(allowed=True)
    
    def check_tool_rules(self, state: AgentState, tool_name: str) -> RuleResult:
        """Check all rules related to tool usage."""
        for rule in self.rules:
            if isinstance(rule, WeatherCheckRule):
                result = rule.check(state, tool_name=tool_name)
                if not result.allowed:
                    return result
        return RuleResult(allowed=True)
    
    def get_rule_descriptions(self) -> list[str]:
        """Get descriptions of all rules for LLM guidance."""
        return [rule.description for rule in self.rules]
    
    def get_rules_summary(self) -> str:
        """Get a formatted summary of all rules."""
        summary = "Business Rules:\n"
        for i, rule in enumerate(self.rules, 1):
            summary += f"{i}. {rule.description}\n"
        return summary


# Global rule engine instance
rule_engine = RuleEngine()


def get_rule_engine() -> RuleEngine:
    """Get the global rule engine instance."""
    return rule_engine
