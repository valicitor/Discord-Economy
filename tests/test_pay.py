import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain import User, GuildConfig
from application import PayCommand, PayCommandRequest
from infrastructure import UserRepository, GuildConfigRepository

class TestPayCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()

        self.guild_config = GuildConfig(data={ 'guild_id': 12344, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12344,
            "username": "TestUser",
             "avatar": "",
            "cash_balance": 100
        })
        self.entity2 = User(guild_id=12344, user_id=2, username="TestUser", avatar="", cash_balance=100)

        # Add test users to the database
        self.guild_config_repository.add(self.guild_config)
        self.user_repository.add(self.entity1)
        self.user_repository.add(self.entity2)

    def tearDown(self):
        # Remove test users from the database
        self.guild_config_repository.delete(self.guild_config)
        self.user_repository.delete(self.entity1)
        self.user_repository.delete(self.entity2)

    def test_pay(self):
        # Arrange
        amount_to_transfer = 50

        request = PayCommandRequest(
            guild_id=self.entity1.guild_id,
            user=self.entity1,
            target=self.entity2,
            amount=amount_to_transfer
        )

        # Act
        response = PayCommand(request).execute()

        # Assert
        self.assertEqual(response.user.cash_balance, self.entity1.cash_balance - amount_to_transfer)
        self.assertEqual(response.target.cash_balance, self.entity2.cash_balance + amount_to_transfer)

if __name__ == "__main__":
    unittest.main()