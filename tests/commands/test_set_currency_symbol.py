import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from domain import GuildConfig
from application import SetCurrencySymbolCommand, SetCurrencySymbolCommandRequest
from infrastructure import GuildConfigRepository

class TestSetCurrencySymbolCommand(unittest.TestCase):
    def setUp(self):
        self.guild_config_repository = GuildConfigRepository(db_path=":memory:")
        
        self.guild_config = GuildConfig(data={ 'guild_id': 12341, 'starting_balance': 0, 'currency_symbol': '$', 'currency_emoji': '' })

        self.guild_config_repository.add(self.guild_config)

    def tearDown(self):
        # Remove test user from the database
        self.guild_config_repository.delete(self.guild_config)

    def test_set_currency_symbol(self):
        # Arrange
        currency_symbol_1="💰"
        currency_symbol_2="<:custom_emoji:123456789012345678>"
        currency_symbol_3="<a:animated_emoji:123456789012345678>"
        currency_symbol_4="£"

        request1 = SetCurrencySymbolCommandRequest(
            guild_id=self.guild_config.guild_id, 
            currency_symbol=currency_symbol_1
        )
        request2 = SetCurrencySymbolCommandRequest(
            guild_id=self.guild_config.guild_id, 
            currency_symbol=currency_symbol_2
        )
        request3 = SetCurrencySymbolCommandRequest(
            guild_id=self.guild_config.guild_id, 
            currency_symbol=currency_symbol_3
        )
        request4 = SetCurrencySymbolCommandRequest(
            guild_id=self.guild_config.guild_id, 
            currency_symbol=currency_symbol_4
        )

        # Act
        response1 = SetCurrencySymbolCommand(request1).execute()
        response2 = SetCurrencySymbolCommand(request2).execute()
        response3 = SetCurrencySymbolCommand(request3).execute()
        response4 = SetCurrencySymbolCommand(request4).execute()

        # Assert
        self.assertEqual(response1.guild_config.currency_emoji, "💰")
        self.assertEqual(response1.guild_config.currency_symbol, "")

        self.assertEqual(response2.guild_config.currency_emoji, "<:custom_emoji:123456789012345678>")
        self.assertEqual(response2.guild_config.currency_symbol, "")
        
        self.assertEqual(response3.guild_config.currency_emoji, "<a:animated_emoji:123456789012345678>")
        self.assertEqual(response3.guild_config.currency_symbol, "")
                
        self.assertEqual(response4.guild_config.currency_emoji, "")
        self.assertEqual(response4.guild_config.currency_symbol, "£")

if __name__ == "__main__":
    unittest.main()