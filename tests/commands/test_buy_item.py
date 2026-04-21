import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import BuyItemCommand, BuyItemCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestBuyItemCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize shared resources for all tests
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        # Cleanup shared resources after all tests. Technically not needed for in-memory, and close_all will shutdown all connections for all repositories, but good practice.
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

    def test_buy_unit_item(self):
        # Arrange
        player = self.default_setup.player_profile1

        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            item_id=1,
            item_name=None
        )

        # Act
        response = asyncio.run(BuyItemCommand(request).execute())

        # Assert
        self.assertEqual(response.shop_item.item_id, 1)
    
    def test_buy_weapon_item(self):
        # Arrange
        player = self.default_setup.player_profile1

        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            item_id=3,
            item_name=None
        )

        # Act
        response = asyncio.run(BuyItemCommand(request).execute())

        # Assert
        self.assertEqual(response.shop_item.item_id, 3)

if __name__ == "__main__":
    unittest.main()