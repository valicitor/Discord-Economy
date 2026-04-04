import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import SetBalanceCommand, SetBalanceCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestSetBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        self.default_setup.setUp()

    def tearDown(self):
        self.default_setup.tearDown()

    def test_set_balance_cash(self):
        # Arrange
        amount = 50
        player = self.default_setup.player_profile1

        request = SetBalanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            account_type="Cash",
            amount=amount
        )

        # Act
        response = SetBalanceCommand(request).execute()

        # Assert
        self.assertEqual(response.player.balances[0].balance, amount)

if __name__ == "__main__":
    unittest.main()