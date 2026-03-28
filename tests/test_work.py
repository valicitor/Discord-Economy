import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain import User, GuildConfig
from domain import OnCooldownException
from application import WorkCommand, WorkCommandRequest
from infrastructure import UserRepository, GuildConfigRepository

class TestWorkCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()
        
        self.guild_config = GuildConfig(data={ 
            'guild_id': 12341, 
            'starting_balance': 0, 
            'currency_symbol': '$', 
            'currency_emoji': '', 
            'work_min_pay': 10, 
            'work_max_pay': 100, 
            'work_cooldown': 60 
        })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12341,
            "username": "TestUser",
            "avatar": "",
            "cash_balance": 100,
            "work_cooldown": 0
        })

        # Add test user to the database
        self.guild_config_repository.add(self.guild_config)
        self.user_repository.add(self.entity1)

    def tearDown(self):
        # Remove test user from the database
        self.guild_config_repository.delete(self.guild_config)
        self.user_repository.delete(self.entity1)

    def test_work_command(self):
        # Arrange
        request = WorkCommandRequest(
            guild_id=self.guild_config.guild_id, 
            user=self.entity1
        )

        # Act
        response = WorkCommand(request).execute()
        print(f"User last work timestamp: {response.user.last_work}")

        # Try to work again, should fail due to cooldown
        with self.assertRaises(OnCooldownException) as context:
            no_response = WorkCommand(request).execute()

        # Assert
        self.assertGreater(response.user.cash_balance, self.entity1.cash_balance)

if __name__ == "__main__":
    unittest.main()