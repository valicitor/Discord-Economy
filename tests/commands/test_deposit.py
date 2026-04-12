import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import DepositCommand, DepositCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestDepositCommand(unittest.TestCase):
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