import sys
import os
import sqlite3

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository,
    FactionRepository,
    FactionMemberRepository
)
from application import DiscordGuild, DiscordUser
from application import GetLeaderboardQuery, GetLeaderboardQueryRequest

from application.helpers.ensure_user import ensure_guild_and_users

class TestGetLeaderboardQuery(unittest.TestCase):
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
        self.discord_user1 = DiscordUser(user_id=67900, name="TestUser1", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67901, name="TestUser2", display_avatar="avatar_url")
        self.discord_user3 = DiscordUser(user_id=67902, name="TestUser3", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2, self.player_profile3] = ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2, self.discord_user3])

        self.player_profile1.balances[0].balance = 1500
        self.player_balance_repository.update(self.player_profile1.balances[0])
        self.player_profile1.bank_accounts[0].balance = 1500
        self.bank_account_repository.update(self.player_profile1.bank_accounts[0])

        self.player_profile2.balances[0].balance = 50
        self.player_balance_repository.update(self.player_profile2.balances[0])
        self.player_profile2.bank_accounts[0].balance = 2000
        self.bank_account_repository.update(self.player_profile2.bank_accounts[0])

        self.player_profile3.balances[0].balance = 2000
        self.player_balance_repository.update(self.player_profile3.balances[0])
        self.player_profile3.bank_accounts[0].balance = 25
        self.bank_account_repository.update(self.player_profile3.bank_accounts[0])

    def tearDown(self):
        # Remove test user from the database
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

    def test_get_leaderboard(self):
        # Arrange
        cash_request = GetLeaderboardQueryRequest(
            guild=self.discord_guild,
            page=1,
            sort_by="Cash"
        )
        bank_request = GetLeaderboardQueryRequest(
            guild=self.discord_guild,
            page=1,
            sort_by="Bank"
        )
        total_request = GetLeaderboardQueryRequest(
            guild=self.discord_guild,
            page=1,
            sort_by="Total"
        )

        # Act
        cash_response = GetLeaderboardQuery(cash_request).execute()
        bank_response = GetLeaderboardQuery(bank_request).execute()
        total_response = GetLeaderboardQuery(total_request).execute()

        # Assert
        self.assertEqual(cash_response.server_config.server.guild_id, 12345)
        self.assertEqual(cash_response.players[0].player.rank, 1)
        self.assertEqual(cash_response.players[0].player.username, "TestUser3")
        self.assertEqual(cash_response.players[0].balances[0].balance, 2000)

        self.assertEqual(bank_response.server_config.server.guild_id, 12345)
        self.assertEqual(bank_response.players[0].player.rank, 1)
        self.assertEqual(bank_response.players[0].player.username, "TestUser2")
        self.assertEqual(bank_response.players[0].bank_accounts[0].balance, 2000)

        self.assertEqual(total_response.server_config.server.guild_id, 12345)
        self.assertEqual(total_response.players[0].player.rank, 1)
        self.assertEqual(total_response.players[0].player.username, "TestUser1")
        self.assertEqual(total_response.players[0].balances[0].balance, 1500)
        self.assertEqual(total_response.players[0].bank_accounts[0].balance, 1500)


if __name__ == "__main__":
    unittest.main()