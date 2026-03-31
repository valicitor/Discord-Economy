from attr import dataclass

from infrastructure import  PlayerBalanceRepository, BankAccountRepository
from application.helpers.ensure_user import ensure_guild_and_user

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import InsufficientFundsException

from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class DepositCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    amount: int = None

@dataclass
class DepositCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    amount: int

class DepositCommand:

    def __init__(self, request: DepositCommandRequest):
        self.request = request

        return

    def execute(self) -> DepositCommandResponse:
        server_config, player_profile = ensure_guild_and_user(self.request.guild, self.request.user)

        default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)
        default_bank_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_bank_id"), None)

        i, balance = next(((idx, obj) for idx, obj in enumerate(player_profile.balances) if obj.currency_id == int(default_currency_id)), (None, None))
        j, bank_account = next(((idx, obj) for idx, obj in enumerate(player_profile.bank_accounts) if obj.bank_id == int(default_bank_id)), (None, None))
        
        balance.balance = int(balance.balance) - self.request.amount
        if balance.balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this deposit.")
    
        bank_account.balance = int(bank_account.balance) + self.request.amount

        balance_success = PlayerBalanceRepository().update(balance)
        if not balance_success:
            raise InsufficientFundsException("Failed to update player balance. Please try again.")
        balance = PlayerBalanceRepository().get_by_id(balance.balance_id)

        bank_account_success = BankAccountRepository().update(bank_account)
        if not bank_account_success:
            raise InsufficientFundsException("Failed to update bank account. Please try again.")
        bank_account = BankAccountRepository().get_by_id(bank_account.account_id)

        player_profile.balances[i] = balance
        player_profile.bank_accounts[j] = bank_account

        return DepositCommandResponse(success=balance_success and bank_account_success, server_config=server_config, player=player_profile, amount=self.request.amount)
