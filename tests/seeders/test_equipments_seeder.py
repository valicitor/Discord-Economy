import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import EquipmentRepository, EquipmentStatRepository, SeedEquipmentsIfEmpty, SeedEquipmentStatsIfEmpty

class TestEquipmentsSeeder(unittest.TestCase):
    def setUp(self):
        self.equipment_repository = EquipmentRepository(seeder=SeedEquipmentsIfEmpty, db_path=":memory:")  # Use in-memory database for testing
        self.equipment_stat_repository = EquipmentStatRepository(seeder=SeedEquipmentStatsIfEmpty, db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.equipment_repository.delete_all()
        self.equipment_stat_repository.delete_all()

    def test_seed_equipments_and_equipment_stats_if_empty(self):
        # Act

        # Assert
        equipments = self.equipment_repository.get_all()
        equipment_stats = self.equipment_stat_repository.get_all()
        self.assertGreater(len(equipments), 0)  # Assuming the seed file has at least 1 equipment
        self.assertGreater(len(equipment_stats), 0)  # Assuming the seed file has at least 1 equipment stat

if __name__ == "__main__":
    print(f"Running tests in {__file__}...")
    unittest.main()