import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import AddBalanceCommand, AddBalanceCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestAddBalanceCommand(unittest.TestCase):
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

    def test_add_balance_cash(self):
        # Arrange
        amount_to_add = 50
        player = self.default_setup.player_profile1
        initial_balance = player.balances[0].balance

        request = AddBalanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            account_type="Cash",
            amount=amount_to_add
        )

        # Act
        response = asyncio.run(AddBalanceCommand(request).execute())

        # Assert
        self.assertEqual(response.player.balances[0].balance, initial_balance + amount_to_add)

    def test_add_balance_bank(self):
        # Arrange
        amount_to_add = 50
        player = self.default_setup.player_profile1
        initial_bank_balance = player.bank_accounts[0].balance

        request = AddBalanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            account_type="Bank",
            amount=amount_to_add
        )

        # Act
        response = asyncio.run(AddBalanceCommand(request).execute())

        # Assert
        self.assertEqual(response.player.bank_accounts[0].balance, initial_bank_balance + amount_to_add)

if __name__ == "__main__":
    unittest.main()