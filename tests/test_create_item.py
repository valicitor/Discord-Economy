import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain import Item, GuildConfig
from application import CreateItemCommand, CreateItemCommandRequest
from infrastructure import ItemRepository, GuildConfigRepository

class TestCreateItemCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.guild_config = GuildConfig(data={ 
            'guild_id': 12341, 
            'starting_balance': 0, 
            'currency_symbol': '$', 
            'currency_emoji': '', 
            'work_min_pay': 10, 
            'work_max_pay': 100, 
            'work_cooldown': 60 
        })

        self.item = Item(data={
                "guild_id": 12341,
                "name": "TestItem",
                "category": "TestCategory",
                "icon": "",
                "price": 100,
                "description": "TestDescription",
                "stock": 10,
                "inventory": True,
                "usable": True,
                "sellable": True
            })

        # Add test item to the database
        self.guild_config_repository.add(self.guild_config)

    def tearDown(self):
        # Remove test item from the database
        self.guild_config_repository.delete(self.guild_config)
        ItemRepository().delete(self.item)

    def test_create_item_command(self):
        # Arrange
        request = CreateItemCommandRequest(
            guild_id=self.guild_config.guild_id, 
            item=self.item
        )

        # Act
        response = CreateItemCommand(request).execute()
        self.item = response.item

        # Assert
        self.assertTrue(response.success)
        self.assertIsNotNone(response.item)
        self.assertEqual(response.item.name, "TestItem")

if __name__ == "__main__":
    unittest.main()