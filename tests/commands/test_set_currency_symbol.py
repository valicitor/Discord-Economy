import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest

from infrastructure import (
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    FactionRepository
)
from application import DiscordGuild
from application import SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest

from application.helpers.ensure_user import ensure_guild

class TestSetCurrencySymbolCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.faction_repository = FactionRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")

        self.server_config = ensure_guild(self.discord_guild)

    def tearDown(self):
        # Remove test user from the database
        self.faction_repository.delete_all(self.server_config.server.server_id)
    
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

    def test_set_currency_symbol(self):
        # Arrange
        currency_symbol_1="💰"
        currency_symbol_2="<:custom_emoji:123456789012345678>"
        currency_symbol_3="<a:animated_emoji:123456789012345678>"
        currency_symbol_4="£"

        request1 = SetCurrencySymbolCommandRequest(
            guild=self.discord_guild, 
            currency_symbol=currency_symbol_1
        )
        request2 = SetCurrencySymbolCommandRequest(
            guild=self.discord_guild, 
            currency_symbol=currency_symbol_2
        )
        request3 = SetCurrencySymbolCommandRequest(
            guild=self.discord_guild, 
            currency_symbol=currency_symbol_3
        )
        request4 = SetCurrencySymbolCommandRequest(
            guild=self.discord_guild, 
            currency_symbol=currency_symbol_4
        )

        # Act
        response1 = SetCurrencySymbolCommand(request1).execute()
        response2 = SetCurrencySymbolCommand(request2).execute()
        response3 = SetCurrencySymbolCommand(request3).execute()
        response4 = SetCurrencySymbolCommand(request4).execute()

        # Assert
        self.assertEqual(response1.currency.emoji, "💰")
        self.assertEqual(response1.currency.symbol, "")

        self.assertEqual(response2.currency.emoji, "<:custom_emoji:123456789012345678>")
        self.assertEqual(response2.currency.symbol, "")
        
        self.assertEqual(response3.currency.emoji, "<a:animated_emoji:123456789012345678>")
        self.assertEqual(response3.currency.symbol, "")
                
        self.assertEqual(response4.currency.emoji, "")
        self.assertEqual(response4.currency.symbol, "£")

if __name__ == "__main__":
    unittest.main()