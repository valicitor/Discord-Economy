import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetShopQuery, GetShopQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetShopQuery(unittest.TestCase):
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

    def test_get_shop_items(self):
        # Arrange
        request = GetShopQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            page=1,
            sort_by="Cost",
            limit=10
        )

        # Act
        response = asyncio.run(GetShopQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)

    def test_get_shop_items_by_name(self):
        # Arrange
        request = GetShopQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            page=1,
            sort_by="Name",
            limit=10
        )

        # Act
        response = asyncio.run(GetShopQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)

    def test_get_shop_items_by_stock(self):
        # Arrange
        request = GetShopQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            page=1,
            sort_by="Stock",
            limit=10
        )

        # Act
        response = asyncio.run(GetShopQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)

if __name__ == "__main__":
    unittest.main()