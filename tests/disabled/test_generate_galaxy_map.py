import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup
from application import GenerateGalaxyMapCommand, GenerateGalaxyMapCommandRequest

class TestGenerateGalaxyMapCommand(unittest.TestCase):
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

    def test_generate_galaxy_map(self):
        # Arrange
        request = GenerateGalaxyMapCommandRequest(
            guild=self.default_setup.discord_guild,
            output_path="test_galaxy_map.png", 
            show_grid=True
        )

        # Act
        response = asyncio.run(GenerateGalaxyMapCommand(request).execute())

        # Assert
        locations = asyncio.run(self.default_setup.location_repository.get_all())
        self.assertGreater(len(locations), 0)  # Assuming the seed file has at least 1 location
        self.assertTrue(response.success)
        self.assertEqual(response.output_path, "test_galaxy_map.png")

if __name__ == "__main__":
    unittest.main()