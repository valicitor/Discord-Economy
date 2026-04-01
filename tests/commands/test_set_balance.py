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
from application import SetBalanceCommand, SetBalanceCommandRequest

from application.helpers.ensure_user import ensure_guild_and_user

class TestSetBalanceCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user = DiscordUser(user_id=68090, name="TestUser", display_avatar="avatar_url")

        self.server_config, self.player_profile = ensure_guild_and_user(self.discord_guild, self.discord_user)

    def tearDown(self):
        # Remove test user from the database
        self.bank_account_repository.delete_all(self.player_profile.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile.player.player_id)
        self.player_repository.delete(self.player_profile.player)
        
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

    def test_set_balance(self):
        # Arrange
        amount = 50

        request = SetBalanceCommandRequest(
            guild=self.discord_guild, 
            user=self.discord_user, 
            account_type="Cash",
            amount=amount
        )

        # Act
        response = SetBalanceCommand(request).execute()

        # Assert
        self.assertEqual(response.player.balances[0].balance, amount)

if __name__ == "__main__":
    unittest.main()