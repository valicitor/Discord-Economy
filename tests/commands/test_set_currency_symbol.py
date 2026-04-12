import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest
from tests.helper.default_setup import DefaultSetup

class TestSetCurrencySymbolCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize shared resources for all tests
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        # Cleanup shared resources after all tests. Technically not needed for in-memory, and close_all will shutdown all connections for all repositories, but good practice.
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

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