import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import BuyItemCommand, BuyItemCommandRequest, SellItemCommand, SellItemCommandRequest
from domain import InvalidDataException
from tests.helper.default_setup import DefaultSetup

class TestSellItemCommand(unittest.TestCase):
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

    def _buy(self, user, item_id, quantity=1):
        request = BuyItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            item_id=item_id,
            item_name=None,
            quantity=quantity
        )
        return asyncio.run(BuyItemCommand(request).execute())

    def _sell(self, user, item_name, quantity=1):
        request = SellItemCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            item_id=None,
            item_name=item_name,
            quantity=quantity
        )
        return asyncio.run(SellItemCommand(request).execute())

    def test_sell_weapon_item(self):
        # Arrange — DC-15A Blaster Rifle (item_id=3) costs 500, player1 has 1500
        buy_response = self._buy(self.default_setup.discord_user1, item_id=3)
        balance_after_buy = buy_response.player.balances[0].balance

        # Act
        sell_response = self._sell(self.default_setup.discord_user1, item_name="DC-15A Blaster Rifle")

        # Assert sell amount is 50% of price
        expected_sell_amount = int(buy_response.shop_item.price * 0.5)
        self.assertEqual(sell_response.sell_amount, expected_sell_amount)

        # Assert balance increased by sell amount
        self.assertEqual(sell_response.player.balances[0].balance, balance_after_buy + expected_sell_amount)

        # Assert item removed from inventory
        inventory = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            sell_response.player.player.player_id, buy_response.shop_item.catalogue_id, status='stored'
        ))
        self.assertIsNone(inventory)

    def test_sell_unit(self):
        # Arrange — Clone Trooper (item_id=1) costs 1000, player1 has 1500
        buy_response = self._buy(self.default_setup.discord_user1, item_id=1)
        balance_after_buy = buy_response.player.balances[0].balance

        # Act
        sell_response = self._sell(self.default_setup.discord_user1, item_name="Clone Trooper")

        # Assert sell amount is 50% of price
        expected_sell_amount = int(buy_response.shop_item.price * 0.5)
        self.assertEqual(sell_response.sell_amount, expected_sell_amount)
        self.assertEqual(sell_response.player.balances[0].balance, balance_after_buy + expected_sell_amount)

        # Assert unit was removed
        unit = asyncio.run(self.default_setup.player_unit_repository.get_by_name(
            "Clone Trooper", sell_response.player.player.player_id
        ))
        self.assertIsNone(unit)

    def test_sell_item_not_owned(self):
        # Arrange — player1 has never bought a DC-15A
        with self.assertRaises(InvalidDataException):
            self._sell(self.default_setup.discord_user1, item_name="DC-15A Blaster Rifle")

    def test_sell_partial_quantity(self):
        # Arrange — buy 2, sell 1, 1 should remain
        self._buy(self.default_setup.discord_user1, item_id=3, quantity=2)
        self._sell(self.default_setup.discord_user1, item_name="DC-15A Blaster Rifle", quantity=1)

        buy_catalogue_id = asyncio.run(self.default_setup.items_repository.get_by_id(3)).catalogue_id
        inventory = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            self.default_setup.player_profile1.player.player_id, buy_catalogue_id, status='stored'
        ))
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.quantity, 1)

if __name__ == "__main__":
    unittest.main()
