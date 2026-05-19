import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import BuyStockCommand, BuyStockCommandRequest
from domain import Business, BusinessStock, InsufficientFundsException, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestBuyStockCommand(unittest.TestCase):
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

    def _create_business_with_stock(self, base_price=100, market_points=100, dividend_rate=0.05):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id

        business = Business(server_id=server_id, name="Test Corp", type="trading", x=0, y=0, range=None)
        business_id = asyncio.run(ds.business_repository.insert(business))

        stock = BusinessStock(business_id=business_id, base_price=base_price, market_points=market_points, dividend_rate=dividend_rate)
        asyncio.run(ds.business_stock_repository.insert(stock))

        return business_id

    def test_buy_stock_success(self):
        # Arrange — current_price = 100 * (100/100) = 100, buy 10 shares = 1000 cost
        business_id = self._create_business_with_stock(base_price=100, market_points=100)
        request = BuyStockCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            business_id=business_id,
            quantity=10
        )

        # Act
        response = asyncio.run(BuyStockCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.quantity, 10)
        self.assertEqual(response.total_cost, 1000)
        self.assertEqual(response.player.balances[0].balance, 500)  # 1500 - 1000

        # Assert stock holding created
        holding = asyncio.run(self.default_setup.player_stock_repository.get_by_player_business(
            response.player.player.player_id, business_id
        ))
        self.assertIsNotNone(holding)
        self.assertEqual(holding.quantity, 10)

    def test_buy_stock_insufficient_funds(self):
        # Arrange — player2 has only 50 cash, cost is 100 * 10 = 1000
        business_id = self._create_business_with_stock(base_price=100)
        request = BuyStockCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user2,
            business_id=business_id,
            quantity=10
        )

        # Act & Assert
        with self.assertRaises(InsufficientFundsException):
            asyncio.run(BuyStockCommand(request).execute())

    def test_buy_stock_business_not_found(self):
        # Arrange — no business with that ID
        request = BuyStockCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            business_id=99999,
            quantity=1
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(BuyStockCommand(request).execute())

    def test_buy_stock_accumulates_existing_holding(self):
        # Arrange — buy 5 shares, then buy 5 more → 10 total
        business_id = self._create_business_with_stock(base_price=100)
        request = BuyStockCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            business_id=business_id,
            quantity=5
        )
        asyncio.run(BuyStockCommand(request).execute())
        asyncio.run(BuyStockCommand(request).execute())

        # Assert single record with quantity=10
        holding = asyncio.run(self.default_setup.player_stock_repository.get_by_player_business(
            self.default_setup.player_profile1.player.player_id, business_id
        ))
        self.assertEqual(holding.quantity, 10)


if __name__ == "__main__":
    unittest.main()
