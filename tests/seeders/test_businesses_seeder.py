import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestBusinessesSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_seed_businesses_and_actions_if_empty(self):
        # Act

        # Assert
        businesses = self.default_setup.business_repository.get_all(self.default_setup.server_config.server.server_id)
        actions = self.default_setup.action_repository.get_all()
        self.assertGreater(len(businesses), 0)  # Assuming the seed file has at least 1 business
        self.assertGreater(len(actions), 0)  # Assuming the seed file has at least 1 action

if __name__ == "__main__":
    print(f"Running tests in {__file__}...")
    unittest.main()