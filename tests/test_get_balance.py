import sys
import os
from unittest.mock import Mock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import GetBalanceQuery
from infrastructure import ServerConfigRepository
from infrastructure import UserRepository

class TestGetBalanceQuery(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.get_balance_query = GetBalanceQuery()

        self.entity1 = {
            "user_id": 1,
            "guild_id": 12346,
            "username": "TestUser",
            "balance": 100
        }
        self.entity2 = {
            "user_id": 2,
            "guild_id": 12346,
            "username": "TestUser",
            "balance": 200
        }

        # Add test users to the database
        asyncio.run(self.server_config_repository.add({ 'guild_id': self.entity1["guild_id"], 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' }))
        asyncio.run(self.user_repository.add(self.entity1))
        asyncio.run(self.user_repository.add(self.entity2))

    def tearDown(self):
        # Remove test users from the database
        asyncio.run(self.server_config_repository.delete({ 'guild_id': self.entity1["guild_id"] }))
        asyncio.run(self.user_repository.delete(self.entity1))
        asyncio.run(self.user_repository.delete(self.entity2))

    def test_pay(self):
        # Arrange
        fake_user1 = Mock()
        fake_user1.id = self.entity1["user_id"]
        fake_user1.name = self.entity1["username"]
        fake_user1.display_name = self.entity1.get("display_name", fake_user1.name)
        fake_user1.mention = f"<@{fake_user1.id}>"
    
        fake_user2 = Mock()
        fake_user2.id = self.entity2["user_id"]
        fake_user2.name = self.entity2["username"]
        fake_user2.display_name = self.entity2.get("display_name", fake_user2.name)
        fake_user2.mention = f"<@{fake_user2.id}>"

        # Assert
        updated_balance1 = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], fake_user1))
        updated_balance2 = asyncio.run(self.get_balance_query.execute(self.entity2["guild_id"], fake_user2))

        self.assertEqual(updated_balance1, 100)
        self.assertEqual(updated_balance2, 200)

if __name__ == "__main__":
    unittest.main()