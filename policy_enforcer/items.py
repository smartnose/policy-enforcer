"""
Item definitions and constants for the policy enforcer.
"""

from enum import Enum
from typing import List


class Item(str, Enum):
    """Available items that can be purchased and owned by users."""
    
    # Gaming equipment
    TV = "TV"
    XBOX = "Xbox"
    
    # Camping equipment
    HIKING_BOOTS = "Hiking Boots"
    
    # Swimming equipment
    GOGGLES = "Goggles"
    
    def __str__(self) -> str:
        """Return the string value of the item."""
        return self.value
    
    # Additional items (for extensibility)
    SUNSCREEN = "Sunscreen"


class ItemRequirements:
    """Item requirements for different activities."""
    
    PLAY_GAMES: List[Item] = [Item.TV, Item.XBOX]
    GO_CAMPING: List[Item] = [Item.HIKING_BOOTS]
    SWIMMING: List[Item] = [Item.GOGGLES]
    
    @classmethod
    def get_requirements_for_activity(cls, activity: str) -> List[Item]:
        """Get required items for a specific activity."""
        from .state import Activity
        
        if activity == Activity.PLAY_GAMES.value:
            return cls.PLAY_GAMES
        elif activity == Activity.GO_CAMPING.value:
            return cls.GO_CAMPING
        elif activity == Activity.SWIMMING.value:
            return cls.SWIMMING
        else:
            return []
    
    @classmethod
    def get_missing_items(cls, activity: str, user_items: set) -> List[Item]:
        """Get missing items for a specific activity."""
        required = cls.get_requirements_for_activity(activity)
        return [item for item in required if item.value not in user_items]
    
    @classmethod
    def is_valid_item(cls, item_name: str) -> bool:
        """Check if an item name is valid."""
        try:
            Item(item_name)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_all_items(cls) -> List[str]:
        """Get all available item names."""
        return [item.value for item in Item]


# Convenience constants for backward compatibility
GAMING_ITEMS = [Item.TV, Item.XBOX]
CAMPING_ITEMS = [Item.HIKING_BOOTS]
SWIMMING_ITEMS = [Item.GOGGLES]
