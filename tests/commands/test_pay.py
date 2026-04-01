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
from application import PayCommand, PayCommandRequest

from application.helpers.ensure_user import ensure_guild_and_users

class TestPayCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user1 = DiscordUser(user_id=67990, name="TestUser", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67991, name="TestUser", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2] = ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2])

        self.player_profile1.balances[0].balance = 100
        self.player_balance_repository.update(self.player_profile1.balances[0])

        self.player_profile2.balances[0].balance = 100
        self.player_balance_repository.update(self.player_profile2.balances[0])

    def tearDown(self):
        # Remove test user from the database
        self.bank_account_repository.delete_all(self.player_profile1.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile1.player.player_id)
        self.player_repository.delete(self.player_profile1.player)
        
        self.bank_account_repository.delete_all(self.player_profile2.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile2.player.player_id)
        self.player_repository.delete(self.player_profile2.player)
        
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

    def test_pay(self):
        # Arrange
        amount_to_transfer = 50

        request = PayCommandRequest(
            guild=self.discord_guild,
            user=self.discord_user1,
            target=self.discord_user2,
            amount=amount_to_transfer
        )

        # Act
        response = PayCommand(request).execute()

        # Assert
        self.assertEqual(response.player.balances[0].balance, 50)
        self.assertEqual(response.target_player.balances[0].balance, 150)

if __name__ == "__main__":
    unittest.main()