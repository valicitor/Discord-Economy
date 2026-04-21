import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestCatalogueSeeder(unittest.TestCase):
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

    def test_seed_catalogue_items_if_empty(self):
        # Act

        # Assert
        catalogue_items = asyncio.run(self.default_setup.catalogue_repository.get_all(self.default_setup.server_config.server.server_id))
        self.assertGreater(len(catalogue_items), 0)  # Assuming the seed file has at least 1 catalogue item

if __name__ == "__main__":
    unittest.main()