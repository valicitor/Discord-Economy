import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import AddBalanceCommand, AddBalanceCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestAddBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

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