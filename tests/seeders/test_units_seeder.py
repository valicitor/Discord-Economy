import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import UnitRepository, UnitStatRepository, SeedUnitsAndUnitStatsIfEmpty

class TestUnitsSeeder(unittest.TestCase):
    def setUp(self):
        self.unit_repository = UnitRepository(db_path=":memory:")  # Use in-memory database for testing
        self.unit_stat_repository = UnitStatRepository(db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.unit_repository.delete_all()
        self.unit_stat_repository.delete_all()

    def test_seed_units_and_unit_stats_if_empty(self):
        # Act
        SeedUnitsAndUnitStatsIfEmpty(self.unit_repository, self.unit_stat_repository)

        # Assert
        units = self.unit_repository.get_all()
        unit_stats = self.unit_stat_repository.get_all()
        self.assertGreater(len(units), 0)  # Assuming the seed file has at least 1 unit
        self.assertGreater(len(unit_stats), 0)  # Assuming the seed file has at least 1 unit stat

if __name__ == "__main__":
    unittest.main()