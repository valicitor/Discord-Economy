import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from domain import User, GuildConfig
from application import PayCommand
from application import GetUserQuery
from infrastructure import UserRepository, GuildConfigRepository

class TestPayCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()
        self.pay_command = PayCommand()
        self.get_user_query = GetUserQuery()

        self.guild_config = GuildConfig(data={ 'guild_id': 12344, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12344,
            "username": "TestUser",
            "cash_balance": 100
        })
        self.entity2 = User(guild_id=12344, user_id=2, username="TestUser", cash_balance=100)

        # Add test users to the database
        asyncio.run(self.guild_config_repository.add(self.guild_config))
        asyncio.run(self.user_repository.add(self.entity1))
        asyncio.run(self.user_repository.add(self.entity2))

    def tearDown(self):
        # Remove test users from the database
        asyncio.run(self.guild_config_repository.delete(self.guild_config))
        asyncio.run(self.user_repository.delete(self.entity1))
        asyncio.run(self.user_repository.delete(self.entity2))

    def test_pay(self):
        # Arrange
        user_original_balance = self.entity1.cash_balance
        target_original_balance = self.entity2.cash_balance
        amount_to_transfer = 50

        # Act
        asyncio.run(self.pay_command.execute(
            self.entity1.guild_id,
            self.entity1,
            self.entity2,
            amount_to_transfer
        ))

        # Assert
        updated_user1 = asyncio.run(self.get_user_query.execute(self.guild_config.guild_id, self.entity1))
        updated_user2 = asyncio.run(self.get_user_query.execute(self.guild_config.guild_id, self.entity2))

        self.assertEqual(updated_user1.cash_balance, user_original_balance - amount_to_transfer)
        self.assertEqual(updated_user2.cash_balance, target_original_balance + amount_to_transfer)

if __name__ == "__main__":
    unittest.main()