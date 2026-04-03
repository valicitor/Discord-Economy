import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import PointOfInterestRepository, SeedPointOfInterestsIfEmpty

class TestPOISeeder(unittest.TestCase):
    def setUp(self):
        self.POI_repository = PointOfInterestRepository(seeder=SeedPointOfInterestsIfEmpty, db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.POI_repository.delete_all()

    def test_seed_point_of_interests_if_empty(self):
        # Act

        # Assert
        pois = self.POI_repository.get_all()
        self.assertGreater(len(pois), 0)  # Assuming the seed file has at least 1 POI

if __name__ == "__main__":
    unittest.main()