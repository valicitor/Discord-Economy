import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain import User, GuildConfig
from application import DepositCommand, DepositCommandRequest
from infrastructure import UserRepository, GuildConfigRepository

class TestDepositCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()

        self.guild_config = GuildConfig(data={ 'guild_id': 12344, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12344,
            "username": "TestUser",
             "avatar": "",
            "cash_balance": 100,
            "bank_balance": 1000
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

    def test_deposit(self):
        # Arrange
        amount_to_deposit = 50

        request = DepositCommandRequest(
            guild_id=self.entity1.guild_id,
            user=self.entity1,
            amount=amount_to_deposit
        )

        # Act
        response = DepositCommand(request).execute()

        # Assert
        self.assertEqual(response.user.cash_balance, self.entity1.cash_balance - amount_to_deposit)
        self.assertEqual(response.user.bank_balance, self.entity1.bank_balance + amount_to_deposit)

if __name__ == "__main__":
    unittest.main()