import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetCatalogueQuery, GetCatalogueQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetCatalogueQuery(unittest.TestCase):
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

    def test_get_catalogue_item_valid(self):
        # Arrange
        request = GetCatalogueQueryRequest(
            guild=self.default_setup.discord_guild,
            name="Droideka Shield Generator"  # Assuming this catalogue item exists in the seeded data
        )

        # Act
        response = asyncio.run(GetCatalogueQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)
        self.assertIsNotNone(response.catalogue_item)


if __name__ == "__main__":
    unittest.main()