import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain import User, GuildConfig
from application import AddBalanceCommand, AddBalanceCommandRequest
from infrastructure import UserRepository, GuildConfigRepository

class TestAddBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()
        
        self.guild_config = GuildConfig(data={ 'guild_id': 12341, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12341,
            "username": "TestUser",
            "avatar": "",
            "cash_balance": 100
        })

        # Add test user to the database
        self.guild_config_repository.add(self.guild_config)
        self.user_repository.add(self.entity1)

    def tearDown(self):
        # Remove test user from the database
        self.guild_config_repository.delete(self.guild_config)
        self.user_repository.delete(self.entity1)

    def test_add_balance(self):
        # Arrange
        amount_to_add = 50

        request = AddBalanceCommandRequest(
            guild_id=self.guild_config.guild_id, 
            user=self.entity1, 
            account_type="Cash",
            amount=amount_to_add
        )

        # Act
        response = AddBalanceCommand(request).execute()

        # Assert
        self.assertEqual(response.user.cash_balance, self.entity1.cash_balance + amount_to_add)

if __name__ == "__main__":
    unittest.main()