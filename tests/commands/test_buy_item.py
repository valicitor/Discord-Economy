import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import BuyItemCommand, BuyItemCommandRequest
from domain import InsufficientFundsException
from tests.helper.default_setup import DefaultSetup

class TestBuyItemCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

    def test_buy_unit_item(self):
        # Arrange — Clone Trooper costs 1000, player1 starts with 1500
        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            item_id=1,
            item_name=None,
            quantity=1
        )

        # Act
        response = asyncio.run(BuyItemCommand(request).execute())

        # Assert item returned
        self.assertEqual(response.shop_item.item_id, 1)
        self.assertTrue(response.success)

        # Assert balance was deducted by item price
        expected_balance = 1500 - response.shop_item.price
        self.assertEqual(response.player.balances[0].balance, expected_balance)

        # Assert unit was added
        unit = asyncio.run(self.default_setup.player_unit_repository.get_by_name("Clone Trooper", response.player.player.player_id))
        self.assertIsNotNone(unit)
        self.assertEqual(unit.quantity, 1)

    def test_buy_weapon_item(self):
        # Arrange — DC-15A Blaster Rifle costs 500, player1 starts with 1500
        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            item_id=3,
            item_name=None,
            quantity=1
        )

        # Act
        response = asyncio.run(BuyItemCommand(request).execute())

        # Assert item returned
        self.assertEqual(response.shop_item.item_id, 3)
        self.assertTrue(response.success)

        # Assert balance was deducted by item price
        expected_balance = 1500 - response.shop_item.price
        self.assertEqual(response.player.balances[0].balance, expected_balance)

        # Assert inventory entry was created
        inventory = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            response.player.player.player_id, response.shop_item.catalogue_id, status='stored'
        ))
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.quantity, 1)

    def test_buy_item_insufficient_funds(self):
        # Arrange — player2 has only 50 cash, Clone Trooper costs 1000
        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user2,
            item_id=1,
            item_name=None,
            quantity=1
        )

        # Act & Assert
        with self.assertRaises(InsufficientFundsException):
            asyncio.run(BuyItemCommand(request).execute())

if __name__ == "__main__":
    unittest.main()
