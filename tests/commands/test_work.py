import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import WorkCommand, WorkCommandRequest
from domain import OnCooldownException
from tests.helper.default_setup import DefaultSetup

class TestWorkCommand(unittest.TestCase):
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

    def test_work(self):
        # Arrange
        player = self.default_setup.player_profile1
        initial_balance = player.balances[0].balance

        request = WorkCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(WorkCommand(request).execute())

        # Assert
        if response.action_success:
            self.assertGreater(response.player.balances[0].balance, initial_balance)
        else:
            self.assertLess(response.player.balances[0].balance, initial_balance)

        with self.assertRaises(OnCooldownException):  # Fails with On cooldown error, which is expected since we just worked
            asyncio.run(WorkCommand(request).execute())

        

if __name__ == "__main__":
    unittest.main()