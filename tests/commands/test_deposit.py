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
    BankAccountRepository,
    FactionRepository,
    FactionMemberRepository
)
from application import DiscordGuild, DiscordUser
from application import DepositCommand, DepositCommandRequest

from application.helpers.ensure_user import ensure_guild_and_user

class TestDepositCommand(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")

        self.faction_repository = FactionRepository(db_path=":memory:")
        self.faction_member_repository = FactionMemberRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user = DiscordUser(user_id=67790, name="TestUser", display_avatar="avatar_url")

        self.server_config, self.player_profile = ensure_guild_and_user(self.discord_guild, self.discord_user)

        self.player_profile.balances[0].balance = 100
        self.player_balance_repository.update(self.player_profile.balances[0])
        self.player_profile.bank_accounts[0].balance = 150
        self.bank_account_repository.update(self.player_profile.bank_accounts[0])

    def tearDown(self):
        # Remove test user from the database
        self.faction_member_repository.delete_by_player_id(self.player_profile.player.player_id)
        self.faction_repository.delete_all(self.server_config.server.server_id)
    
        self.bank_account_repository.delete_all(self.player_profile.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile.player.player_id)
        self.player_repository.delete(self.player_profile.player)
        
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

    def test_deposit(self):
        # Arrange
        amount_to_deposit = 50

        deposit_request = DepositCommandRequest(
            guild=self.discord_guild,
            user=self.discord_user,
            amount=amount_to_deposit
        )

        # Act
        response = DepositCommand(deposit_request).execute()

        # Assert
        self.assertEqual(response.player.balances[0].balance, 50)
        self.assertEqual(response.player.bank_accounts[0].balance, 200)


if __name__ == "__main__":
    unittest.main()