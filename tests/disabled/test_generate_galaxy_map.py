import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest

from domain import Faction, FactionMember, PointOfInterest
from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository,
    PointOfInterestRepository,
    FactionRepository,
    FactionMemberRepository
)
from infrastructure import PointOfInterestSeeder
from application import DiscordGuild, DiscordUser
from application import GenerateGalaxyMapCommand, GenerateGalaxyMapCommandRequest

from application.helpers.ensure_user import ensure_guild_and_users
from tests.helper.default_setup import DefaultSetup

class TestGenerateGalaxyMapCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_generate_galaxy_map(self):
        # Arrange
        request = GenerateGalaxyMapCommandRequest(
            guild=self.default_setup.discord_guild,
            output_path="test_galaxy_map.png", 
            show_grid=True
        )

        # Act
        response = GenerateGalaxyMapCommand(request).execute()

        # Assert
        locations = self.default_setup.location_repository.get_all()
        self.assertGreater(len(locations), 0)  # Assuming the seed file has at least 1 location
        self.assertTrue(response.success)
        self.assertEqual(response.output_path, "test_galaxy_map.png")

if __name__ == "__main__":
    unittest.main()