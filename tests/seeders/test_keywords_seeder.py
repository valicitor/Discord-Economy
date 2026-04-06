import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from tests.helper.default_setup import DefaultSetup

class TestKeywordsSeeder(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_seed_keywords_if_empty(self):
        # Act

        # Assert
        keywords = asyncio.run(self.default_setup.keyword_repository.get_all(self.default_setup.server_config.server.server_id))

        self.assertGreater(len(keywords), 0)  # Assuming the seed file has at least 1 keyword

if __name__ == "__main__":
    unittest.main()