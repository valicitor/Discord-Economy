import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import RaceRepository, RaceStatRepository, SeedRacesAndRaceStatsIfEmpty

class TestRacesSeeder(unittest.TestCase):
    def setUp(self):
        self.race_repository = RaceRepository(":memory:")  # Use in-memory database for testing
        self.race_stat_repository = RaceStatRepository(":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.race_repository.delete_all()
        self.race_stat_repository.delete_all()

    def test_seed_races_and_race_stats_if_empty(self):
        # Act
        SeedRacesAndRaceStatsIfEmpty(self.race_repository, self.race_stat_repository)

        # Assert
        races = self.race_repository.get_all()
        race_stats = self.race_stat_repository.get_all()
        self.assertGreater(len(races), 0)  # Assuming the seed file has at least 1 race
        self.assertGreater(len(race_stats), 0)  # Assuming the seed file has at least 1 race stat

if __name__ == "__main__":
    unittest.main()