import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestRacesSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_seed_races_and_race_stats_if_empty(self):
        # Act

        # Assert
        races = asyncio.run(self.default_setup.race_repository.get_all(self.default_setup.server_config.server.server_id))
        race_stats = asyncio.run(self.default_setup.race_stat_repository.get_all(None))
        self.assertGreater(len(races), 0)  # Assuming the seed file has at least 1 race
        self.assertGreater(len(race_stats), 0)  # Assuming the seed file has at least 1 race stat

if __name__ == "__main__":
    unittest.main()