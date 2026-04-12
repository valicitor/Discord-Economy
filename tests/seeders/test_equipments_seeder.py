import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestEquipmentsSeeder(unittest.TestCase):
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

    def test_seed_equipments_and_equipment_stats_if_empty(self):
        # Act

        # Assert
        equipments = asyncio.run(self.default_setup.equipment_repository.get_all(self.default_setup.server_config.server.server_id))
        equipment_stats = asyncio.run(self.default_setup.equipment_stat_repository.get_all(None))
        self.assertGreater(len(equipments), 0)  # Assuming the seed file has at least 1 equipment
        self.assertGreater(len(equipment_stats), 0)  # Assuming the seed file has at least 1 equipment stat

if __name__ == "__main__":
    unittest.main()