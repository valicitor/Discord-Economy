import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetStocksQuery, GetStocksQueryRequest
from domain import Business, BusinessStock, PlayerStock
from tests.helper.default_setup import DefaultSetup


class TestGetStocksQuery(unittest.TestCase):
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

    def _create_business_with_stock(self):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id

        business = Business(server_id=server_id, name="Test Corp", type="trading", x=0, y=0, range=None)
        business_id = asyncio.run(ds.business_repository.insert(business))

        stock = BusinessStock(business_id=business_id, base_price=200, market_points=100, dividend_rate=0.05)
        asyncio.run(ds.business_stock_repository.insert(stock))

        return business_id

    def test_get_stocks_empty_portfolio(self):
        # Arrange — player1 holds no stocks
        request = GetStocksQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(GetStocksQuery(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(len(response.holdings), 0)

    def test_get_stocks_with_holdings(self):
        # Arrange — player1 holds 5 shares of a business
        business_id = self._create_business_with_stock()
        player_id = self.default_setup.player_profile1.player.player_id

        holding = PlayerStock(player_id=player_id, business_id=business_id, quantity=5)
        asyncio.run(self.default_setup.player_stock_repository.insert(holding))

        request = GetStocksQueryRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(GetStocksQuery(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(len(response.holdings), 1)

        player_stock, business_stock, business = response.holdings[0]
        self.assertEqual(player_stock.quantity, 5)
        self.assertEqual(business.name, "Test Corp")
        self.assertEqual(business_stock.base_price, 200)


if __name__ == "__main__":
    unittest.main()
