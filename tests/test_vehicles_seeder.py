import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import VehicleRepository, VehicleStatRepository, SeedVehiclesAndVehicleStatsIfEmpty

class TestVehiclesSeeder(unittest.TestCase):
    def setUp(self):
        self.vehicle_repository = VehicleRepository(":memory:")  # Use in-memory database for testing
        self.vehicle_stat_repository = VehicleStatRepository(":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.vehicle_repository.delete_all()
        self.vehicle_stat_repository.delete_all()

    def test_seed_vehicles_and_vehicle_stats_if_empty(self):
        # Act
        SeedVehiclesAndVehicleStatsIfEmpty(self.vehicle_repository, self.vehicle_stat_repository)

        # Assert
        vehicles = self.vehicle_repository.get_all()
        vehicle_stats = self.vehicle_stat_repository.get_all()
        self.assertGreater(len(vehicles), 0)  # Assuming the seed file has at least 1 vehicle
        self.assertGreater(len(vehicle_stats), 0)  # Assuming the seed file has at least 1 vehicle stat

if __name__ == "__main__":
    unittest.main()