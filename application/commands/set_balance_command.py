from attr import dataclass

from infrastructure import  PlayerBalanceRepository, BankAccountRepository
from application.helpers.ensure_user import ensure_guild_and_user

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import UpdateFailedException

@dataclass
class SetBalanceCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    account_type: str
    amount: int

@dataclass
class SetBalanceCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    account_type: str
    amount: int

class SetBalanceCommand:

    def __init__(self, request: SetBalanceCommandRequest):
        self.request = request

        return

    def execute(self) -> SetBalanceCommandResponse:
        server_config, player_profile = ensure_guild_and_user(self.request.guild, self.request.user)

        if self.request.account_type == "Cash":
            default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)

            i, balance = next(((idx, obj) for idx, obj in enumerate(player_profile.balances) if obj.currency_id == int(default_currency_id)), (None, None))
            balance.balance = self.request.amount

            success = PlayerBalanceRepository().update(balance)
            if not success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            
            balance = PlayerBalanceRepository().get_by_id(balance.balance_id)

            player_profile.balances[i] = balance
        elif self.request.account_type == "Bank":
            default_bank_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_bank_id"), None)

            i, bank_account = next(((idx, obj) for idx, obj in enumerate(player_profile.bank_accounts) if obj.bank_id == int(default_bank_id)), (None, None))
            bank_account.balance = self.request.amount

            success = BankAccountRepository().update(bank_account)
            if not success:
                raise UpdateFailedException("Failed to update bank account. Please try again.")
            
            bank_account = BankAccountRepository().get_by_id(bank_account.account_id)

            player_profile.bank_accounts[i] = bank_account

        return SetBalanceCommandResponse(success=success, server_config=server_config, player=player_profile, account_type=self.request.account_type, amount=self.request.amount)
