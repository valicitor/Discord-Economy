import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetEquipmentQuery, GetEquipmentQueryRequest
from tests.helper.default_setup import DefaultSetup

class GetEquipmentQueryQuery(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_get_equipment_valid(self):
        # Arrange
        server_config = self.default_setup.server_config

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