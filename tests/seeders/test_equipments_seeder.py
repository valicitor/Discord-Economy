import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestEquipmentsSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_seed_equipments_and_equipment_stats_if_empty(self):
        # Act

        # Assert
        equipments = self.default_setup.equipment_repository.get_all(self.default_setup.server_config.server.server_id)
        equipment_stats = self.default_setup.equipment_stat_repository.get_all()
        self.assertGreater(len(equipments), 0)  # Assuming the seed file has at least 1 equipment
        self.assertGreater(len(equipment_stats), 0)  # Assuming the seed file has at least 1 equipment stat

if __name__ == "__main__":
    print(f"Running tests in {__file__}...")
    unittest.main()