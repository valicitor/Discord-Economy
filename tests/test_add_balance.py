import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest

from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository
)
from application import DiscordGuild, DiscordUser
from application import AddBalanceCommand, AddBalanceCommandRequest

class TestAddBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user = DiscordUser(user_id=67890, name="TestUser", display_avatar="avatar_url")

    def tearDown(self):
        # Remove test user from the database
        pass

    def test_add_balance(self):
        # Arrange
        amount_to_add = 50

        cash_request = AddBalanceCommandRequest(
            guild=self.discord_guild,
            user=self.discord_user,
            account_type="Cash",
            amount=amount_to_add
        )
        bank_request = AddBalanceCommandRequest(
            guild=self.discord_guild,
            user=self.discord_user,
            account_type="Bank",
            amount=amount_to_add
        )

        # Act
        cash_response = AddBalanceCommand(cash_request).execute()
        bank_response = AddBalanceCommand(bank_request).execute()

        # Assert
        self.assertEqual(cash_response.player.balances[0].balance, amount_to_add)
        self.assertEqual(bank_response.player.bank_accounts[0].balance, amount_to_add)

if __name__ == "__main__":
    unittest.main()