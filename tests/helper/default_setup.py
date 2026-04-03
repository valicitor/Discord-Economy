from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository,
    FactionRepository,
    FactionMemberRepository,
    PlayerActionRepository
)
from application import DiscordGuild, DiscordUser
from application.helpers.ensure_user import ensure_guild_and_users

class DefaultSetup:

    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")
        self.faction_repository = FactionRepository(db_path=":memory:")

        self.player_repository = PlayerRepository(db_path=":memory:")
        self.player_balance_repository = PlayerBalanceRepository(db_path=":memory:")
        self.bank_account_repository = BankAccountRepository(db_path=":memory:")
        self.faction_member_repository = FactionMemberRepository(db_path=":memory:")
        self.player_action_repository = PlayerActionRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        self.discord_user1 = DiscordUser(user_id=67900, name="TestUser1", display_avatar="avatar_url")
        self.discord_user2 = DiscordUser(user_id=67901, name="TestUser2", display_avatar="avatar_url")
        self.discord_user3 = DiscordUser(user_id=67902, name="TestUser3", display_avatar="avatar_url")

        self.server_config, [self.player_profile1, self.player_profile2, self.player_profile3] = ensure_guild_and_users(self.discord_guild, [self.discord_user1, self.discord_user2, self.discord_user3])

        self.player_profile1.balances[0].balance = 1500
        self.player_balance_repository.update(self.player_profile1.balances[0])
        self.player_profile1.bank_accounts[0].balance = 1500
        self.bank_account_repository.update(self.player_profile1.bank_accounts[0])

        self.player_profile2.balances[0].balance = 50
        self.player_balance_repository.update(self.player_profile2.balances[0])
        self.player_profile2.bank_accounts[0].balance = 2000
        self.bank_account_repository.update(self.player_profile2.bank_accounts[0])

        self.player_profile3.balances[0].balance = 2000
        self.player_balance_repository.update(self.player_profile3.balances[0])
        self.player_profile3.bank_accounts[0].balance = 25
        self.bank_account_repository.update(self.player_profile3.bank_accounts[0])

    def tearDown(self):
        # Remove test user from the database
        self.player_action_repository.delete_all(self.player_profile1.player.player_id)
        self.player_action_repository.delete_all(self.player_profile2.player.player_id)
        self.player_action_repository.delete_all(self.player_profile3.player.player_id)
        self.faction_member_repository.delete_by_player_id(self.player_profile1.player.player_id)
        self.faction_member_repository.delete_by_player_id(self.player_profile2.player.player_id)
        self.faction_member_repository.delete_by_player_id(self.player_profile3.player.player_id)
        self.bank_account_repository.delete_all(self.player_profile1.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile1.player.player_id)
        self.player_repository.delete(self.player_profile1.player)

        self.bank_account_repository.delete_all(self.player_profile2.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile2.player.player_id)
        self.player_repository.delete(self.player_profile2.player)

        self.bank_account_repository.delete_all(self.player_profile3.player.player_id)
        self.player_balance_repository.delete_all(self.player_profile3.player.player_id)
        self.player_repository.delete(self.player_profile3.player)

        self.faction_repository.delete_all(self.server_config.server.server_id)
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)