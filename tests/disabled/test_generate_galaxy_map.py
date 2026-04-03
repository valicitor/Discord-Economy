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

class TestGenerateGalaxyMapCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")

        self.faction_repository = FactionRepository(db_path=":memory:")
        self.faction_member_repository = FactionMemberRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user1 = DiscordUser(user_id=67890, name="TestUser1", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67891, name="TestUser2", display_avatar="avatar_url")
        self.discord_user3 = DiscordUser(user_id=67892, name="TestUser3", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2, self.player_profile3] = ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2, self.discord_user3])

        self.POI_repository = PointOfInterestRepository(seeder=PointOfInterestSeeder(self.server_config.server.server_id), db_path=":memory:")  # Use in-memory database for testing

        _, enemy_faction_id = self.faction_repository.add(Faction(name="Enemy Faction", description="Enemy", color="#FF0000", owner_id=self.player_profile3.player.player_id, server_id=self.server_config.server.server_id))
        _, member_id = self.faction_member_repository.add(FactionMember(faction_id=enemy_faction_id, player_id=self.player_profile3.player.player_id, role="Leader"))

        poi = self.POI_repository.get_all()[0]
        poi.owner_player_id = self.player_profile3.player.player_id
        self.POI_repository.update(poi)

        _, ally_faction_id = self.faction_repository.add(Faction(name="Ally Faction", description="Ally", color="#00FF00", owner_id=self.player_profile1.player.player_id, server_id=self.server_config.server.server_id))
        _, member_id = self.faction_member_repository.add(FactionMember(faction_id=ally_faction_id, player_id=self.player_profile1.player.player_id, role="Leader"))

        poi = self.POI_repository.get_all()[2]
        poi.owner_player_id = self.player_profile1.player.player_id
        self.POI_repository.update(poi)

    def tearDown(self):
        self.POI_repository.delete_all()

        self.faction_member_repository.delete_by_player_id(self.player_profile1.player.player_id)
        self.faction_member_repository.delete_by_player_id(self.player_profile2.player.player_id)
        self.faction_member_repository.delete_by_player_id(self.player_profile3.player.player_id)
        self.faction_repository.delete_all(self.server_config.server.server_id)

        self.bank_account_repository.delete_all(self.player_profile1.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile1.player.player_id)
        self.player_repository.delete(self.player_profile1.player)

        self.bank_account_repository.delete_all(self.player_profile2.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile2.player.player_id)
        self.player_repository.delete(self.player_profile2.player)

        self.bank_account_repository.delete_all(self.player_profile3.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile3.player.player_id)
        self.player_repository.delete(self.player_profile3.player)
        
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

    def test_generate_galaxy_map(self):
        # Arrange
        request = GenerateGalaxyMapCommandRequest(
            output_path="test_galaxy_map.png", 
            show_grid=True
        )

        # Act
        response = GenerateGalaxyMapCommand(request).execute()

        # Assert
        pois = self.POI_repository.get_all()
        self.assertGreater(len(pois), 0)  # Assuming the seed file has at least 1 POI

        self.assertTrue(response.success)
        self.assertEqual(response.output_path, "test_galaxy_map.png")

if __name__ == "__main__":
    unittest.main()