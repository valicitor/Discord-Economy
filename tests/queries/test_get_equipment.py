import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetEquipmentQuery, GetEquipmentQueryRequest
from tests.helper.default_setup import DefaultSetup

class GetEquipmentQueryQuery(unittest.TestCase):
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

    def test_get_equipment_valid(self):
        # Arrange
        request = GetEquipmentQueryRequest(
            guild=self.default_setup.discord_guild,
            name="Droideka Shield Generator"  # Assuming this equipment exists in the seeded data
        )

        # Act
        response = asyncio.run(GetEquipmentQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)
        self.assertIsNotNone(response.equipment)
        self.assertIsInstance(response.stats, list)


if __name__ == "__main__":
    unittest.main()