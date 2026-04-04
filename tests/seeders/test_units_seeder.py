import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestUnitsSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_seed_units_and_unit_stats_if_empty(self):
        # Act

        # Assert
        units = self.default_setup.unit_repository.get_all(self.default_setup.server_config.server.server_id)
        unit_stats = self.default_setup.unit_stat_repository.get_all()
        self.assertGreater(len(units), 0)  # Assuming the seed file has at least 1 unit
        self.assertGreater(len(unit_stats), 0)  # Assuming the seed file has at least 1 unit stat

if __name__ == "__main__":
    unittest.main()