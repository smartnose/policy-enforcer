"""
Unit tests for the items module.
"""

import unittest
from policy_enforcer.items import Item, ItemRequirements


class TestItem(unittest.TestCase):
    """Test the Item enum."""
    
    def test_item_values(self):
        """Test that items have correct values."""
        self.assertEqual(Item.TV.value, "TV")
        self.assertEqual(Item.XBOX.value, "Xbox")
        self.assertEqual(Item.HIKING_BOOTS.value, "Hiking Boots")
        self.assertEqual(Item.GOGGLES.value, "Goggles")
        self.assertEqual(Item.SUNSCREEN.value, "Sunscreen")
    
    def test_item_string_enum(self):
        """Test that items can be used as strings."""
        self.assertIsInstance(Item.TV, str)
        self.assertEqual(str(Item.TV), "TV")


class TestItemRequirements(unittest.TestCase):
    """Test the ItemRequirements class."""
    
    def test_activity_requirements(self):
        """Test activity item requirements."""
        self.assertEqual(ItemRequirements.PLAY_GAMES, [Item.TV, Item.XBOX])
        self.assertEqual(ItemRequirements.GO_CAMPING, [Item.HIKING_BOOTS])
        self.assertEqual(ItemRequirements.SWIMMING, [Item.GOGGLES])
    
    def test_is_valid_item(self):
        """Test item validation."""
        self.assertTrue(ItemRequirements.is_valid_item("TV"))
        self.assertTrue(ItemRequirements.is_valid_item("Xbox"))
        self.assertTrue(ItemRequirements.is_valid_item("Hiking Boots"))
        self.assertTrue(ItemRequirements.is_valid_item("Goggles"))
        self.assertTrue(ItemRequirements.is_valid_item("Sunscreen"))
        
        self.assertFalse(ItemRequirements.is_valid_item("Invalid Item"))
        self.assertFalse(ItemRequirements.is_valid_item(""))
        self.assertFalse(ItemRequirements.is_valid_item(None))
    
    def test_get_all_items(self):
        """Test getting all available items."""
        all_items = ItemRequirements.get_all_items()
        expected = ["TV", "Xbox", "Hiking Boots", "Goggles", "Sunscreen"]
        self.assertEqual(sorted(all_items), sorted(expected))
    
    def test_get_missing_items_play_games(self):
        """Test missing items for playing games."""
        # Empty inventory
        missing = ItemRequirements.get_missing_items("Play games", set())
        self.assertEqual(set(missing), {Item.TV, Item.XBOX})
        
        # Partial inventory
        missing = ItemRequirements.get_missing_items("Play games", {"TV"})
        self.assertEqual(set(missing), {Item.XBOX})
        
        # Complete inventory
        missing = ItemRequirements.get_missing_items("Play games", {"TV", "Xbox"})
        self.assertEqual(missing, [])
    
    def test_get_missing_items_camping(self):
        """Test missing items for camping."""
        # Empty inventory
        missing = ItemRequirements.get_missing_items("Go Camping", set())
        self.assertEqual(missing, [Item.HIKING_BOOTS])
        
        # Complete inventory
        missing = ItemRequirements.get_missing_items("Go Camping", {"Hiking Boots"})
        self.assertEqual(missing, [])
    
    def test_get_missing_items_swimming(self):
        """Test missing items for swimming."""
        # Empty inventory
        missing = ItemRequirements.get_missing_items("Swimming", set())
        self.assertEqual(missing, [Item.GOGGLES])
        
        # Complete inventory
        missing = ItemRequirements.get_missing_items("Swimming", {"Goggles"})
        self.assertEqual(missing, [])
    
    def test_get_missing_items_invalid_activity(self):
        """Test missing items for invalid activity."""
        missing = ItemRequirements.get_missing_items("Invalid Activity", set())
        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()
