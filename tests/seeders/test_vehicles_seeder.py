import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestVehiclesSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_seed_vehicles_and_vehicle_stats_if_empty(self):
        # Act

        # Assert
        vehicles = asyncio.run(self.default_setup.vehicle_repository.get_all(self.default_setup.server_config.server.server_id))
        vehicle_stats = asyncio.run(self.default_setup.vehicle_stat_repository.get_all(None))
        self.assertGreater(len(vehicles), 0)  # Assuming the seed file has at least 1 vehicle
        self.assertGreater(len(vehicle_stats), 0)  # Assuming the seed file has at least 1 vehicle stat

if __name__ == "__main__":
    unittest.main()