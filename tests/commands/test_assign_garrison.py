import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import AssignGarrisonCommand, AssignGarrisonCommandRequest
from domain import PlayerUnit, RecordNotFoundException, InvalidDataException
from tests.helper.default_setup import DefaultSetup


class TestAssignGarrisonCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

    def _create_unit(self, player_id, unit_name="Test Unit"):
        unit = PlayerUnit(player_id=player_id, name=unit_name, quantity=5, custom=True)
        return asyncio.run(self.default_setup.player_unit_repository.insert(unit))

    def test_assign_garrison_success(self):
        # Arrange — create a unit for player1, POI "Capital World" is seeded
        player_id = self.default_setup.player_profile1.player.player_id
        self._create_unit(player_id, "Test Unit")

        request = AssignGarrisonCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            unit_name="Test Unit",
            poi_name="Capital World"
        )

        # Act
        response = asyncio.run(AssignGarrisonCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.unit.name, "Test Unit")
        self.assertEqual(response.poi.name, "Capital World")
        self.assertIsNotNone(response.garrison.garrison_id)

    def test_assign_garrison_unit_not_found(self):
        # Arrange — no unit with that name
        request = AssignGarrisonCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            unit_name="Nonexistent Unit",
            poi_name="Capital World"
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(AssignGarrisonCommand(request).execute())

    def test_assign_garrison_poi_not_found(self):
        # Arrange — create unit but use bad POI name
        player_id = self.default_setup.player_profile1.player.player_id
        self._create_unit(player_id, "Test Unit B")

        request = AssignGarrisonCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            unit_name="Test Unit B",
            poi_name="Nonexistent POI"
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(AssignGarrisonCommand(request).execute())

    def test_assign_garrison_already_garrisoned(self):
        # Arrange — assign unit, then try to assign it again
        player_id = self.default_setup.player_profile1.player.player_id
        self._create_unit(player_id, "Test Unit C")

        request = AssignGarrisonCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            unit_name="Test Unit C",
            poi_name="Capital World"
        )
        asyncio.run(AssignGarrisonCommand(request).execute())

        # Act & Assert — second assignment raises error
        with self.assertRaises(InvalidDataException):
            asyncio.run(AssignGarrisonCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
