import sys
import os
from unittest.mock import Mock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import AddBalanceCommand
from application import GetBalanceQuery
from infrastructure import UserRepository, ServerConfigRepository

class TestAddBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.add_balance_command = AddBalanceCommand()
        self.get_balance_query = GetBalanceQuery()

        self.entity1 = {
            "user_id": 1,
            "guild_id": 12345,
            "username": "TestUser",
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
        fake_user = Mock()
        fake_user.id = self.entity1["user_id"]
        fake_user.name = self.entity1["username"]
        fake_user.display_name = self.entity1.get("display_name", fake_user.name)
        fake_user.mention = f"<@{fake_user.id}>"
    
        amount_to_add = 50

        # Act
        asyncio.run(self.add_balance_command.execute(self.entity1["guild_id"], fake_user, amount_to_add))

        # Assert
        updated_balance = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], fake_user))
        self.assertEqual(updated_balance, self.entity1["balance"] + amount_to_add)

if __name__ == "__main__":
    unittest.main()