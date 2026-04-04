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

        _, enemy_faction_id = self.default_setup.faction_repository.add(Faction(name="Enemy Faction", description="Enemy", color="#FF0000", owner_id=self.default_setup.player_profile3.player.player_id, server_id=self.default_setup.server_config.server.server_id))
        self.default_setup.faction_member_repository.delete_by_player_id(self.default_setup.player_profile3.player.player_id)  # Remove existing faction membership
        _, member_id = self.default_setup.faction_member_repository.add(FactionMember(faction_id=enemy_faction_id, player_id=self.default_setup.player_profile3.player.player_id, role="Leader"))

        poi = self.default_setup.POI_repository.get_all(self.default_setup.server_config.server.server_id)[0]
        poi.owner_player_id = self.default_setup.player_profile3.player.player_id
        self.default_setup.POI_repository.update(poi)

        _, ally_faction_id = self.default_setup.faction_repository.add(Faction(name="Ally Faction", description="Ally", color="#00FF00", owner_id=self.default_setup.player_profile1.player.player_id, server_id=self.default_setup.server_config.server.server_id))
        self.default_setup.faction_member_repository.delete_by_player_id(self.default_setup.player_profile1.player.player_id)  # Remove existing faction membership
        _, member_id = self.default_setup.faction_member_repository.add(FactionMember(faction_id=ally_faction_id, player_id=self.default_setup.player_profile1.player.player_id, role="Leader"))

        poi = self.default_setup.POI_repository.get_all(self.default_setup.server_config.server.server_id)[2]
        poi.owner_player_id = self.default_setup.player_profile1.player.player_id
        self.default_setup.POI_repository.update(poi)

    def tearDown(self):
        self.default_setup.tearDown()

    def test_generate_galaxy_map(self):
        # Arrange
        request = GenerateGalaxyMapCommandRequest(
            server_id=self.default_setup.server_config.server.server_id,
            output_path="test_galaxy_map.png", 
            show_grid=True
        )

        # Act
        response = GenerateGalaxyMapCommand(request).execute()

        # Assert
        pois = self.default_setup.POI_repository.get_all(self.default_setup.server_config.server.server_id)
        self.assertGreater(len(pois), 0)  # Assuming the seed file has at least 1 POI

        self.assertTrue(response.success)
        self.assertEqual(response.output_path, "test_galaxy_map.png")

if __name__ == "__main__":
    unittest.main()