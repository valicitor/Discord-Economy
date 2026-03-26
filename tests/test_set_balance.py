import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from domain import User, GuildConfig
from application import SetBalanceCommand
from application import GetUserQuery
from infrastructure import UserRepository, GuildConfigRepository

class TestSetBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()
        self.set_balance_command = SetBalanceCommand()
        self.get_user_query = GetUserQuery()

        self.guild_config = GuildConfig(data={ 'guild_id': 12345, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={"user_id": 1, "guild_id": 12345, "username": "TestUser", "cash_balance": 100 })

        # Add test user to the database
        asyncio.run(self.guild_config_repository.add(self.guild_config))
        asyncio.run(self.user_repository.add(self.entity1))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.guild_config_repository.delete(self.guild_config))
        asyncio.run(self.user_repository.delete(self.entity1))

    def test_add_balance(self):
        # Arrange
        amount = 50

        # Act
        asyncio.run(self.set_balance_command.execute(self.guild_config.guild_id, self.entity1, amount))

        # Assert
        updated_user = asyncio.run(self.get_user_query.execute(self.guild_config.guild_id, self.entity1))
        self.assertEqual(updated_user.cash_balance, amount)

if __name__ == "__main__":
    unittest.main()