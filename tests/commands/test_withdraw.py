import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import WithdrawCommand, WithdrawCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestWithdrawCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_valid_withdraw(self):
        # Arrange
        amount_to_withdraw = 50
        player = self.default_setup.player_profile1
        initial_balance = player.balances[0].balance
        initial_bank_balance = player.bank_accounts[0].balance

        withdraw_request = WithdrawCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_withdraw
        )

        # Act
        response = WithdrawCommand(withdraw_request).execute()

        # Assert
        self.assertEqual(response.player.balances[0].balance, initial_balance + amount_to_withdraw)
        self.assertEqual(response.player.bank_accounts[0].balance, initial_bank_balance - amount_to_withdraw)

    def test_negative_withdraw(self):
        # Arrange
        amount_to_withdraw = -50
        withdraw_request = WithdrawCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_withdraw
        )

        # Act & Assert
        with self.assertRaises(ValueError):  # Assuming ValueError is raised for invalid withdrawals
            WithdrawCommand(withdraw_request).execute()

    def test_zero_withdraw(self):
        # Arrange
        amount_to_withdraw = 0
        withdraw_request = WithdrawCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=amount_to_withdraw
        )

        # Act & Assert
        with self.assertRaises(ValueError):  # Assuming ValueError is raised for invalid withdrawals
            WithdrawCommand(withdraw_request).execute()

if __name__ == "__main__":
    unittest.main()