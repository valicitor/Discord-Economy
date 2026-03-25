import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import SetBalanceCommand
from application import GetTopBalancesQuery
from infrastructure import ServerConfigRepository
from infrastructure import UserRepository

class TestGetTopBalancesQuery(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.set_balance_command = SetBalanceCommand()
        self.get_top_balances_query = GetTopBalancesQuery()

        self.entity1 = {
            "user_id": 1,
            "guild_id": 12349,
            "balance": 10
        }
        self.entity2 = {
            "user_id": 2,
            "guild_id": 12349,
            "balance": 50
        }
        self.entity3 = {
            "user_id": 3,
            "guild_id": 12349,
            "balance": 100
        }
        self.entity4 = {
            "user_id": 4,
            "guild_id": 12349,
            "balance": 9
        }

        # Add test user to the database
        asyncio.run(self.server_config_repository.add({ 'guild_id': self.entity1["guild_id"], 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' }))
        asyncio.run(self.user_repository.add(self.entity1))
        asyncio.run(self.user_repository.add(self.entity2))
        asyncio.run(self.user_repository.add(self.entity3))
        asyncio.run(self.user_repository.add(self.entity4))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.server_config_repository.delete({ 'guild_id': self.entity1["guild_id"] }))
        asyncio.run(self.user_repository.delete(self.entity1))
        asyncio.run(self.user_repository.delete(self.entity2))
        asyncio.run(self.user_repository.delete(self.entity3))
        asyncio.run(self.user_repository.delete(self.entity4))

    def test_add_balance(self):
        # Arrange
        amount = 3

        # Act
        asyncio.run(self.get_top_balances_query.execute(self.entity1["guild_id"], amount))

        # Assert
        top_users = asyncio.run(self.get_top_balances_query.execute(self.entity1["guild_id"], amount))
        top_user = top_users[0]

        self.assertEqual(top_user['user_id'], self.entity3['user_id'])
        self.assertEqual(len(top_users), amount)

if __name__ == "__main__":
    unittest.main()