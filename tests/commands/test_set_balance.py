import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import SetBalanceCommand, SetBalanceCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestSetBalanceCommand(unittest.TestCase):
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

    def test_set_balance_cash(self):
        # Arrange
        amount = 50

        request = SetBalanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            account_type="Cash",
            amount=amount
        )

        # Act
        response = asyncio.run(SetBalanceCommand(request).execute())

        # Assert
        self.assertEqual(response.player.balances[0].balance, amount)

if __name__ == "__main__":
    unittest.main()