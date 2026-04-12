import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetBalanceQuery, GetBalanceQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetBalanceQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize shared resources for all tests
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        # Cleanup shared resources after all tests. Technically not needed for in-memory, and close_all will shutdown all connections for all repositories, but good practice.
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

    def test_get_balance_valid(self):
        # Arrange
        player = self.default_setup.player_profile1
        initial_balance = player.balances[0].balance
        initial_bank_balance = player.bank_accounts[0].balance

        request = GetBalanceQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
        )

        # Act
        response = asyncio.run(GetBalanceQuery(request).execute())

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)
        self.assertEqual(response.player.balances[0].balance, initial_balance)
        self.assertEqual(response.player.bank_accounts[0].balance, initial_bank_balance)


if __name__ == "__main__":
    unittest.main()