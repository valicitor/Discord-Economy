from attr import dataclass

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from domain import InsufficientFundsException, UpdateFailedException
from infrastructure import  PlayerBalanceRepository, BankAccountRepository
from application.helpers.helpers import Helpers

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

    async def execute(self) -> DepositCommandResponse:
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.bank_account_repository = await BankAccountRepository().get_instance()
    
        if self.request.amount is None or self.request.amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        server_config, player_profile = await Helpers.ensure_guild_and_user(self.request.guild, self.request.user)

        async with self.player_balance_repository.transaction():
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            _, default_bank = server_config.server_settings.get_by_key("default_bank_id")

            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
            j, bank_account = player_profile.bank_accounts.get_by_bank_id(int(default_bank.value))
            
            balance.balance = int(balance.balance) - self.request.amount
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to complete this deposit.")
        
            bank_account.balance = int(bank_account.balance) + self.request.amount

            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            balance = await self.player_balance_repository.get_by_id(balance.balance_id)

            bank_account_success = await self.bank_account_repository.update(bank_account)
            if not bank_account_success:
                raise UpdateFailedException("Failed to update bank account. Please try again.")
            bank_account = await self.bank_account_repository.get_by_id(bank_account.account_id)

            player_profile.balances[i] = balance
            player_profile.bank_accounts[j] = bank_account

        return DepositCommandResponse(success=balance_success and bank_account_success, server_config=server_config, player=player_profile, amount=self.request.amount)
