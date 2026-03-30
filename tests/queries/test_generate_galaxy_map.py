import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GenerateGalaxyMapCommand, GenerateGalaxyMapCommandRequest
from infrastructure import PointOfInterestRepository, SeedPointOfInterestsIfEmpty

class TestGenerateGalaxyMapCommand(unittest.TestCase):
    def setUp(self):
        self.POI_repository = PointOfInterestRepository(db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        self.POI_repository.delete_all()

    def test_generate_galaxy_map(self):
        # Arrange
        SeedPointOfInterestsIfEmpty(self.POI_repository)

        request = GenerateGalaxyMapCommandRequest(
            output_path="test_galaxy_map.png", 
            show_grid=True
        )

        # Act
        # response = GenerateGalaxyMapCommand(request).execute()

        # Assert
        # pois = self.POI_repository.get_all()
        # self.assertGreater(len(pois), 0)  # Assuming the seed file has at least 1 POI

        # self.assertTrue(response.success)
        # self.assertEqual(response.output_path, "test_galaxy_map.png")

if __name__ == "__main__":
    unittest.main()