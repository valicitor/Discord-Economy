import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetBalanceQuery, GetBalanceQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetBalanceQuery(unittest.TestCase):
    def setUp(self):
        self.defaultSetup = DefaultSetup()
        self.defaultSetup.setUp()

    def tearDown(self):
        self.defaultSetup.tearDown()

    def test_get_balance_valid(self):
        # Arrange
        player = self.defaultSetup.player_profile1
        initial_balance = player.balances[0].balance
        initial_bank_balance = player.bank_accounts[0].balance

        request = GetBalanceQueryRequest(
            guild=self.defaultSetup.discord_guild,
            user=self.defaultSetup.discord_user1,
        )

        # Act
        response = GetBalanceQuery(request).execute()

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)
        self.assertEqual(response.player.balances[0].balance, initial_balance)
        self.assertEqual(response.player.bank_accounts[0].balance, initial_bank_balance)


if __name__ == "__main__":
    unittest.main()