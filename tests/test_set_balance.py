import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import SetBalanceCommand
from application import GetBalanceQuery
from infrastructure import ServerConfigRepository
from infrastructure import UserRepository

class TestSetBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.set_balance_command = SetBalanceCommand()
        self.get_balance_query = GetBalanceQuery()

        self.entity1 = {
            "user_id": 1,
            "guild_id": 12348,
            "balance": 100
        }

        # Add test user to the database
        asyncio.run(self.server_config_repository.add({ 'guild_id': self.entity1["guild_id"], 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' }))
        asyncio.run(self.user_repository.add(self.entity1))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.server_config_repository.delete({ 'guild_id': self.entity1["guild_id"] }))
        asyncio.run(self.user_repository.delete(self.entity1))

    def test_add_balance(self):
        # Arrange
        amount = 50

        # Act
        asyncio.run(self.set_balance_command.execute(self.entity1["guild_id"], self.entity1["user_id"], amount))

        # Assert
        updated_balance = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], self.entity1["user_id"]))
        self.assertEqual(updated_balance, amount)

if __name__ == "__main__":
    unittest.main()