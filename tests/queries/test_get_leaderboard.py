import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetLeaderboardQuery, GetLeaderboardQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetLeaderboardQuery(unittest.TestCase):
    def setUp(self):
        self.defaultSetup = DefaultSetup()
        self.defaultSetup.setUp()

    def tearDown(self):
        self.defaultSetup.tearDown()

    def test_get_leaderboard_cash(self):
        # Arrange
        request = GetLeaderboardQueryRequest(
            guild=self.defaultSetup.discord_guild,
            page=1,
            sort_by="Cash"
        )

        # Act
        cash_response = GetLeaderboardQuery(request).execute()

        # Assert
        self.assertEqual(cash_response.server_config.server.guild_id, 12345)
        self.assertEqual(cash_response.players[0].player.rank, 1)
        self.assertEqual(cash_response.players[0].player.username, "TestUser3")
        self.assertEqual(cash_response.players[0].balances[0].balance, 2000)

    def test_get_leaderboard_bank(self):
        # Arrange
        request = GetLeaderboardQueryRequest(
            guild=self.defaultSetup.discord_guild,
            page=1,
            sort_by="Bank"
        )

        # Act
        bank_response = GetLeaderboardQuery(request).execute()

        # Assert
        self.assertEqual(bank_response.server_config.server.guild_id, 12345)
        self.assertEqual(bank_response.players[0].player.rank, 1)
        self.assertEqual(bank_response.players[0].player.username, "TestUser2")
        self.assertEqual(bank_response.players[0].bank_accounts[0].balance, 2000)

    def test_get_leaderboard_total(self):
        # Arrange
        request = GetLeaderboardQueryRequest(
            guild=self.defaultSetup.discord_guild,
            page=1,
            sort_by="Total"
        )

        # Act
        total_response = GetLeaderboardQuery(request).execute()

        # Assert
        self.assertEqual(total_response.server_config.server.guild_id, 12345)
        self.assertEqual(total_response.players[0].player.rank, 1)
        self.assertEqual(total_response.players[0].player.username, "TestUser1")
        self.assertEqual(total_response.players[0].balances[0].balance, 1500)
        self.assertEqual(total_response.players[0].bank_accounts[0].balance, 1500)

if __name__ == "__main__":
    unittest.main()