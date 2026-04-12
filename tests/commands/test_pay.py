import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))


import unittest
from application import PayCommand, PayCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestPayCommand(unittest.TestCase):
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
        
    def test_pay_valid(self):
        # Arrange
        amount_to_transfer = 50
        payer = self.default_setup.player_profile1
        recipient = self.default_setup.player_profile2
        initial_payer_balance = payer.balances[0].balance
        initial_recipient_balance = recipient.balances[0].balance

        request = PayCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            target=self.default_setup.discord_user2,
            amount=amount_to_transfer
        )

        # Act
        response = asyncio.run(PayCommand(request).execute())

        # Assert
        self.assertEqual(response.player.balances[0].balance, initial_payer_balance - amount_to_transfer)
        self.assertEqual(response.target_player.balances[0].balance, initial_recipient_balance + amount_to_transfer)

if __name__ == "__main__":
    unittest.main()