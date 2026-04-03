from attr import dataclass

from infrastructure import  PlayerBalanceRepository, BankAccountRepository, ServerSettingRepository
from application.helpers.ensure_user import ensure_guild_and_user

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import InsufficientFundsException, UpdateFailedException

from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class WithdrawCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    amount: int = None

@dataclass
class WithdrawCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    amount: int

class WithdrawCommand:

    def __init__(self, request: WithdrawCommandRequest):
        self.request = request

        return

    def execute(self) -> WithdrawCommandResponse:
        server_config, player_profile = ensure_guild_and_user(self.request.guild, self.request.user)

        _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
        _, default_bank = server_config.server_settings.get_by_key("default_bank_id")

        i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
        j, bank_account = player_profile.bank_accounts.get_by_bank_id(int(default_bank.value))
        
        bank_account.balance = int(bank_account.balance) - self.request.amount
        if bank_account.balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this withdrawal.")
        balance.balance = int(balance.balance) + self.request.amount

        balance_success = PlayerBalanceRepository().update(balance)
        if not balance_success:
            raise UpdateFailedException("Failed to update player balance. Please try again.")
        balance = PlayerBalanceRepository().get_by_id(balance.balance_id)

        bank_account_success = BankAccountRepository().update(bank_account)
        if not bank_account_success:
            raise UpdateFailedException("Failed to update bank account. Please try again.")
        bank_account = BankAccountRepository().get_by_id(bank_account.account_id)

        player_profile.balances[i] = balance
        player_profile.bank_accounts[j] = bank_account

        return WithdrawCommandResponse(success=balance_success and bank_account_success, server_config=server_config, player=player_profile, amount=self.request.amount)
