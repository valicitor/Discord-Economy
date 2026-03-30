import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from domain import User, GuildConfig
from application import GetBalanceQuery, GetBalanceQueryRequest
from infrastructure import UserRepository, GuildConfigRepository

class TestGetBalanceQuery(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository(":memory:")
        self.user_repository = UserRepository(":memory:")

        self.guild_config = GuildConfig(data={ 'guild_id': 12342, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })
        self.entity1 = User(data={
            "user_id": 1,
            "guild_id": 12342,
            "username": "TestUser",
            "avatar": "",
            "cash_balance": 100,
            "bank_balance": 1100
        })
        self.entity2 = User(data={
            "user_id": 2,
            "guild_id": 12342,
            "username": "TestUser",
            "avatar": "",
            "cash_balance": 200,
            "bank_balance": 1200
        })

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
        request1 = GetBalanceQueryRequest(
            guild_id=self.guild_config.guild_id, 
            user=self.entity1
        )
        request2 = GetBalanceQueryRequest(
            guild_id=self.guild_config.guild_id, 
            user=self.entity2
        )

        # Act
        response1 = GetBalanceQuery(request1).execute()
        response2 = GetBalanceQuery(request2).execute()

        # Assert
        self.assertEqual(response1.user.guild_id, 12342)
        self.assertEqual(response2.user.guild_id, 12342)

        self.assertEqual(response1.user.cash_balance, 100)
        self.assertEqual(response2.user.cash_balance, 200)

        self.assertEqual(response1.user.bank_balance, 1100)
        self.assertEqual(response2.user.bank_balance, 1200)

        self.assertEqual(response1.user.rank, 2)
        self.assertEqual(response2.user.rank, 1)


if __name__ == "__main__":
    unittest.main()