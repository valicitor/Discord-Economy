import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
from application import AddBalanceCommand
from application import GetBalanceQuery
from infrastructure import UserRepository, ServerConfigRepository

class TestAddBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.server_config_repository = ServerConfigRepository()
        self.user_repository = UserRepository()
        self.add_balance_command = AddBalanceCommand(server_config_repository=self.server_config_repository, user_repository=self.user_repository)
        self.get_balance_query = GetBalanceQuery(server_config_repository=self.server_config_repository, user_repository=self.user_repository)

        self.entity1 = {
            "id": 1,
            "guild_id": 12345,
            "balance": 100
        }

        # Add test user to the database
        asyncio.run(self.server_config_repository.add({ 'id': self.entity1["guild_id"], 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' }))
        asyncio.run(self.user_repository.add(self.entity1))

    def tearDown(self):
        # Remove test user from the database
        asyncio.run(self.server_config_repository.delete({ 'id': self.entity1["guild_id"] }))
        asyncio.run(self.user_repository.delete(self.entity1))

    def test_add_balance(self):
        # Arrange
        amount_to_add = 50

        # Act
        asyncio.run(self.add_balance_command.execute(self.entity1["guild_id"], self.entity1["id"], amount_to_add))

        # Assert
        updated_balance = asyncio.run(self.get_balance_query.execute(self.entity1["guild_id"], self.entity1["id"]))
        self.assertEqual(updated_balance, self.entity1["balance"] + amount_to_add)

if __name__ == "__main__":
    unittest.main()