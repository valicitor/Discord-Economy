import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import ExchangeCommand, ExchangeCommandRequest
from domain import Currency, PlayerBalance, ExchangeRate, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestExchangeCommand(unittest.TestCase):
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

    def _setup_second_currency(self, rate: float):
        ds = self.default_setup
        _, default_currency = ds.server_config.server_settings.get_by_key("default_currency_id")
        self.currency1_id = int(default_currency.value)
        server_id = ds.server_config.server.server_id

        credits = Currency(server_id=server_id, name="Credits", emoji="💳", symbol="CR")
        self.currency2_id = asyncio.run(ds.currency_repository.insert(credits))

        balance = PlayerBalance(player_id=ds.player_profile1.player.player_id, currency_id=self.currency2_id, balance=0)
        asyncio.run(ds.player_balance_repository.insert(balance))

        exchange_rate = ExchangeRate(
            server_id=server_id,
            from_currency_id=self.currency1_id,
            to_currency_id=self.currency2_id,
            rate=rate
        )
        asyncio.run(ds.exchange_rate_repository.insert(exchange_rate))

    def test_exchange_success(self):
        # Arrange — rate=2.0, player1 exchanges 100 Cash → 200 Credits
        self._setup_second_currency(rate=2.0)
        request = ExchangeCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            from_currency_id=self.currency1_id,
            to_currency_id=self.currency2_id,
            amount=100
        )

        # Act
        response = asyncio.run(ExchangeCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.amount_spent, 100)
        self.assertEqual(response.amount_received, 200)

        # Cash reduced by 100, credits increased by 200
        _, cash_balance = response.player.balances.get_by_currency_id(self.currency1_id)
        _, credits_balance = response.player.balances.get_by_currency_id(self.currency2_id)
        self.assertEqual(cash_balance.balance, 1400)  # 1500 - 100
        self.assertEqual(credits_balance.balance, 200)

    def test_exchange_no_rate(self):
        # Arrange — no exchange rate exists for this pair
        ds = self.default_setup
        _, default_currency = ds.server_config.server_settings.get_by_key("default_currency_id")
        currency1_id = int(default_currency.value)

        request = ExchangeCommandRequest(
            guild=ds.discord_guild,
            user=ds.discord_user1,
            from_currency_id=currency1_id,
            to_currency_id=9999,
            amount=100
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(ExchangeCommand(request).execute())

    def test_exchange_insufficient_funds(self):
        # Arrange — player2 has 50 cash, tries to exchange 100
        self._setup_second_currency(rate=1.0)

        balance = PlayerBalance(player_id=self.default_setup.player_profile2.player.player_id, currency_id=self.currency2_id, balance=0)
        asyncio.run(self.default_setup.player_balance_repository.insert(balance))

        request = ExchangeCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user2,
            from_currency_id=self.currency1_id,
            to_currency_id=self.currency2_id,
            amount=100  # player2 only has 50
        )

        # Act & Assert
        from domain import InsufficientFundsException
        with self.assertRaises(InsufficientFundsException):
            asyncio.run(ExchangeCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
