import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from domain import User, GuildConfig
from application import SetBalanceCommand
from application import GetTopBalancesQuery
from infrastructure import UserRepository, GuildConfigRepository

class TestGetTopBalancesQuery(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository()
        self.user_repository = UserRepository()
        self.set_balance_command = SetBalanceCommand()
        self.get_top_balances_query = GetTopBalancesQuery()

        self.guild_config = GuildConfig(data={ 'guild_id': 12343, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={ "user_id": 1, "guild_id": 12343, "username": "TestUser", "cash_balance": 100 })
        self.entity2 = User(data={ "user_id": 2, "guild_id": 12343, "username": "TestUser", "cash_balance": 150 })
        self.entity3 = User(data={ "user_id": 3, "guild_id": 12343, "username": "TestUser", "cash_balance": 200 })
        self.entity4 = User(data={ "user_id": 4, "guild_id": 12343, "username": "TestUser", "cash_balance": 250 })
        self.entity5 = User(data={ "user_id": 5, "guild_id": 12343, "username": "TestUser", "cash_balance": 300 })
        self.entity6 = User(data={ "user_id": 6, "guild_id": 12343, "username": "TestUser", "cash_balance": 350 })
        self.entity7 = User(data={ "user_id": 7, "guild_id": 12343, "username": "TestUser", "cash_balance": 400 })
        self.entity8 = User(data={ "user_id": 8, "guild_id": 12343, "username": "TestUser", "cash_balance": 450 })
        self.entity9 = User(data={ "user_id": 9, "guild_id": 12343, "username": "TestUser", "cash_balance": 500 })
        self.entity10 = User(data={ "user_id": 10, "guild_id": 12343, "username": "TestUser", "cash_balance": 550 })
        self.entity11 = User(data={ "user_id": 11, "guild_id": 12343, "username": "TestUser", "cash_balance": 600 })
        self.entity12 = User(data={ "user_id": 12, "guild_id": 12343, "username": "TestUser", "cash_balance": 650 })

        # Add test user to the database
        asyncio.run(self.guild_config_repository.add(self.guild_config))
        asyncio.run(self.user_repository.add(self.entity1))
        asyncio.run(self.user_repository.add(self.entity2))
        asyncio.run(self.user_repository.add(self.entity3))
        asyncio.run(self.user_repository.add(self.entity4))
        asyncio.run(self.user_repository.add(self.entity5))
        asyncio.run(self.user_repository.add(self.entity6))
        asyncio.run(self.user_repository.add(self.entity7))
        asyncio.run(self.user_repository.add(self.entity8))
        asyncio.run(self.user_repository.add(self.entity9))
        asyncio.run(self.user_repository.add(self.entity10))
        asyncio.run(self.user_repository.add(self.entity11))
        asyncio.run(self.user_repository.add(self.entity12))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.guild_config_repository.delete(self.guild_config))
        asyncio.run(self.user_repository.delete(self.entity1))
        asyncio.run(self.user_repository.delete(self.entity2))
        asyncio.run(self.user_repository.delete(self.entity3))
        asyncio.run(self.user_repository.delete(self.entity4))
        asyncio.run(self.user_repository.delete(self.entity5))
        asyncio.run(self.user_repository.delete(self.entity6))
        asyncio.run(self.user_repository.delete(self.entity7))
        asyncio.run(self.user_repository.delete(self.entity8))
        asyncio.run(self.user_repository.delete(self.entity9))
        asyncio.run(self.user_repository.delete(self.entity10))
        asyncio.run(self.user_repository.delete(self.entity11))
        asyncio.run(self.user_repository.delete(self.entity12))

    def test_add_balance(self):
        # Arrange
        page = 1
        sort_by = 'Cash'

        # Act
        top_users = asyncio.run(self.get_top_balances_query.execute(self.guild_config.guild_id, page = page, sort_by = sort_by))
        top_user = top_users[0]

        # Assert
        self.assertEqual(top_user.user_id, self.entity12.user_id)
        self.assertEqual(len(top_users), 10)

if __name__ == "__main__":
    unittest.main()