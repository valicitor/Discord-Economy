from attr import dataclass

from infrastructure import  PlayerBalanceRepository, BankAccountRepository
from application.helpers.ensure_user import ensure_guild_and_user

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

@dataclass
class AddBalanceCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    account_type: str
    amount: int

@dataclass
class AddBalanceCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    account_type: str
    amount: int

class AddBalanceCommand:

    def __init__(self, request: AddBalanceCommandRequest):
        self.request = request

        return

    def execute(self) -> AddBalanceCommandResponse:
        server_config, player_profile = ensure_guild_and_user(self.request.guild, self.request.user)

        if self.request.account_type == "Cash":
            default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)

            i, balance = next(((idx, obj) for idx, obj in enumerate(player_profile.balances) if obj.currency_id == int(default_currency_id)), (None, None))
            balance.balance = int(balance.balance) + self.request.amount

            success = PlayerBalanceRepository().update(balance)
            balance = PlayerBalanceRepository().get_by_id(balance.balance_id)

            player_profile.balances[i] = balance
        elif self.request.account_type == "Bank":
            default_bank_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_bank_id"), None)

            i, bank_account = next(((idx, obj) for idx, obj in enumerate(player_profile.bank_accounts) if obj.bank_id == int(default_bank_id)), (None, None))
            bank_account.balance = int(bank_account.balance) + self.request.amount

            success = BankAccountRepository().update(bank_account)
            bank_account = BankAccountRepository().get_by_id(bank_account.account_id)

            player_profile.bank_accounts[i] = bank_account

        return AddBalanceCommandResponse(success=success, server_config=server_config, player=player_profile, account_type=self.request.account_type, amount=self.request.amount)
