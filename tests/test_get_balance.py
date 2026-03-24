import sys
import os

from infrastructure.persistence import user_repository

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application.queries.get_balance_query import GetBalanceQuery
from infrastructure.persistence.user_repository import UserRepository

class TestGetBalanceQuery(unittest.TestCase):
    def setUp(self):
        self.user_repository = UserRepository()
        self.get_balance_query = GetBalanceQuery(self.user_repository)

        self.entity1 = {
            "id": 1,
            "guild_id": 12345,
            "balance": 100
        }
        self.entity2 = {
            "id": 2,
            "guild_id": 12345,
            "balance": 200
        }

        # Add test users to the database
        asyncio.run(self.user_repository.add(self.entity1))
        asyncio.run(self.user_repository.add(self.entity2))

    def tearDown(self):
        # Remove test users from the database
        asyncio.run(self.user_repository.delete(self.entity1))
        asyncio.run(self.user_repository.delete(self.entity2))

    def test_pay(self):
        # Assert
        updated_balance1 = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], self.entity1["id"]))
        updated_balance2 = asyncio.run(self.get_balance_query.execute(self.entity2["guild_id"], self.entity2["id"]))

        self.assertEqual(updated_balance1, 100)
        self.assertEqual(updated_balance2, 200)

if __name__ == "__main__":
    unittest.main()