import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestSetCurrencySymbolCommand(unittest.TestCase):
    def setUp(self):
        self.default_setup = DefaultSetup()
        asyncio.run(self.default_setup.setUp())

    def tearDown(self):
        asyncio.run(self.default_setup.tearDown())

    def test_set_currency_symbol_valid(self):
        # Arrange
        currency_symbols = [
            ("💰", ""),
            ("<:custom_emoji:123456789012345678>", ""),
            ("<a:animated_emoji:123456789012345678>", ""),
            ("", "£")
        ]

        for emoji, symbol in currency_symbols:
            with self.subTest(emoji=emoji, symbol=symbol):
                request = SetCurrencySymbolCommandRequest(
                    guild=self.default_setup.discord_guild,
                    currency_symbol=emoji or symbol
                )

                # Act
                response = asyncio.run(SetCurrencySymbolCommand(request).execute())

                # Assert
                self.assertEqual(response.currency.emoji, emoji)
                self.assertEqual(response.currency.symbol, symbol)

if __name__ == "__main__":
    unittest.main()