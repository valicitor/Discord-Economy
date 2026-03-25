import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import PayCommand
from application import GetBalanceQuery
from infrastructure import ServerConfigRepository
from infrastructure import UserRepository

class TestPayCommand(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.pay_command = PayCommand()
        self.get_balance_query = GetBalanceQuery()

        self.entity1 = {
            "user_id": 1,
            "guild_id": 12347,
            "balance": 100
        }
        self.entity2 = {
            "user_id": 2,
            "guild_id": 12347,
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
        amount_to_transfer = 50

        # Act
        asyncio.run(self.pay_command.execute(
            self.entity1["guild_id"],
            self.entity1["user_id"],
            self.entity2["user_id"],
            amount_to_transfer
        ))

        # Assert
        updated_balance1 = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], self.entity1["user_id"]))
        updated_balance2 = asyncio.run(self.get_balance_query.execute(self.entity2["guild_id"], self.entity2["user_id"]))

        self.assertEqual(updated_balance1, self.entity1["balance"] - amount_to_transfer)
        self.assertEqual(updated_balance2, self.entity2["balance"] + amount_to_transfer)

if __name__ == "__main__":
    unittest.main()