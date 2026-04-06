import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import DepositCommand, DepositCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestDepositCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_valid_deposit(self):
        # Arrange
        amount_to_deposit = 50
        player = self.default_setup.player_profile1
        initial_balance = player.balances[0].balance
        initial_bank_balance = player.bank_accounts[0].balance

        deposit_request = DepositCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_deposit
        )

        # Act
        response = asyncio.run(DepositCommand(deposit_request).execute())

        # Assert
        self.assertEqual(response.player.balances[0].balance, initial_balance - amount_to_deposit)
        self.assertEqual(response.player.bank_accounts[0].balance, initial_bank_balance + amount_to_deposit)

    def test_negative_deposit(self):
        # Arrange
        amount_to_deposit = -50
        deposit_request = DepositCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_deposit
        )

        # Act & Assert
        with self.assertRaises(ValueError):  # Assuming ValueError is raised for invalid deposits
            asyncio.run(DepositCommand(deposit_request).execute())

    def test_zero_deposit(self):
        # Arrange
        amount_to_deposit = 0
        deposit_request = DepositCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_deposit
        )

        # Act & Assert
        with self.assertRaises(ValueError):  # Assuming ValueError is raised for invalid deposits
            asyncio.run(DepositCommand(deposit_request).execute())



if __name__ == "__main__":
    unittest.main()