import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import PayDividendsCommand, PayDividendsCommandRequest
from domain import Business, BusinessStock, PlayerStock, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestPayDividendsCommand(unittest.TestCase):
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

    def _create_business_with_stock(self, dividend_rate=0.1, base_price=100, market_points=100):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id

        business = Business(server_id=server_id, name="Dividend Corp", type="trading", x=0, y=0, range=None)
        business_id = asyncio.run(ds.business_repository.insert(business))

        stock = BusinessStock(business_id=business_id, base_price=base_price, market_points=market_points, dividend_rate=dividend_rate)
        asyncio.run(ds.business_stock_repository.insert(stock))

        return business_id

    def test_pay_dividends_success(self):
        # Arrange — player1 holds 10 shares, price=100, dividend_rate=0.1
        # payout = int(100 * 0.1 * 10) = 100
        business_id = self._create_business_with_stock(dividend_rate=0.1, base_price=100)
        player_id = self.default_setup.player_profile1.player.player_id

        holding = PlayerStock(player_id=player_id, business_id=business_id, quantity=10)
        asyncio.run(self.default_setup.player_stock_repository.insert(holding))

        request = PayDividendsCommandRequest(
            guild=self.default_setup.discord_guild,
            business_id=business_id
        )

        # Act
        response = asyncio.run(PayDividendsCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.recipients, 1)
        self.assertEqual(response.total_paid, 100)

        # Assert player balance increased
        updated_balance = asyncio.run(
            self.default_setup.player_balance_repository.get_by_id(
                self.default_setup.player_profile1.balances[0].balance_id
            )
        )
        self.assertEqual(updated_balance.balance, 1600)  # 1500 + 100

    def test_pay_dividends_no_stockholders(self):
        # Arrange — business has stock but no player holders
        business_id = self._create_business_with_stock(dividend_rate=0.1)
        request = PayDividendsCommandRequest(
            guild=self.default_setup.discord_guild,
            business_id=business_id
        )

        # Act
        response = asyncio.run(PayDividendsCommand(request).execute())

        # Assert — success but zero recipients
        self.assertTrue(response.success)
        self.assertEqual(response.recipients, 0)
        self.assertEqual(response.total_paid, 0)

    def test_pay_dividends_business_not_found(self):
        # Arrange — no business with that ID
        request = PayDividendsCommandRequest(
            guild=self.default_setup.discord_guild,
            business_id=99999
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(PayDividendsCommand(request).execute())

    def test_pay_dividends_no_stock(self):
        # Arrange — business exists but has no stock listing
        ds = self.default_setup
        business = Business(server_id=ds.server_config.server.server_id, name="Unstocked Corp", type="trading", x=0, y=0, range=None)
        business_id = asyncio.run(ds.business_repository.insert(business))

        request = PayDividendsCommandRequest(
            guild=ds.discord_guild,
            business_id=business_id
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(PayDividendsCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
