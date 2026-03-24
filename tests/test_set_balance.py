import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application.commands.set_balance_command import SetBalanceCommand
from application.queries.get_balance_query import GetBalanceQuery
from infrastructure.persistence.user_repository import UserRepository

class TestSetBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.user_repository = UserRepository()
        self.set_balance_command = SetBalanceCommand(self.user_repository)
        self.get_balance_query = GetBalanceQuery(self.user_repository)

        self.entity1 = {
            "id": 1,
            "guild_id": 12345,
            "balance": 100
        }

        # Add test user to the database
        asyncio.run(self.user_repository.add(self.entity1))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.user_repository.delete(self.entity1))

    def test_add_balance(self):
        # Arrange
        amount = 50

        # Act
        asyncio.run(self.set_balance_command.execute(self.entity1["guild_id"], self.entity1["id"], amount))

        # Assert
        updated_balance = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], self.entity1["id"]))
        self.assertEqual(updated_balance, amount)

if __name__ == "__main__":
    unittest.main()