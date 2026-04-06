from attr import dataclass

from domain.models.player_balance import PlayerBalance
from infrastructure import  PlayerBalanceRepository, BankAccountRepository, ServerSettingRepository
from application.helpers.ensure_user import ensure_guild_and_user

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import UpdateFailedException

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

    async def execute(self) -> AddBalanceCommandResponse:
        server_config, player_profile = await ensure_guild_and_user(self.request.guild, self.request.user)

        if self.request.account_type == "Cash":
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
            balance.balance = int(balance.balance) + self.request.amount

            success = await PlayerBalanceRepository().update(balance)
            if not success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            
            balance = await PlayerBalanceRepository().get_by_id(balance.balance_id)

            player_profile.balances[i] = balance
        elif self.request.account_type == "Bank":
            _, default_bank = server_config.server_settings.get_by_key("default_bank_id")

            i, bank_account = player_profile.bank_accounts.get_by_bank_id(int(default_bank.value))
            bank_account.balance = int(bank_account.balance) + self.request.amount

            success = await BankAccountRepository().update(bank_account)
            if not success:
                raise UpdateFailedException("Failed to update bank account. Please try again.")
            
            bank_account = await BankAccountRepository().get_by_id(bank_account.account_id)

            player_profile.bank_accounts[i] = bank_account

        return AddBalanceCommandResponse(success=success, server_config=server_config, player=player_profile, account_type=self.request.account_type, amount=self.request.amount)
