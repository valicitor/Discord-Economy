from attr import dataclass

from infrastructure import LoanRepository, PlayerBalanceRepository, BankRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Loan, PermissionDeniedException, InvalidDataException, RecordNotFoundException, InsufficientFundsException, UpdateFailedException

@dataclass
class RepayLoanCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    amount: int

@dataclass
class RepayLoanCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    loan: Loan
    amount_paid: int

class RepayLoanCommand:

    def __init__(self, request: RepayLoanCommandRequest):
        self.request = request

    async def execute(self) -> RepayLoanCommandResponse:
        self.loan_repository = await LoanRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.bank_repository = await BankRepository().get_instance()

        if self.request.amount <= 0:
            raise InvalidDataException("Repayment amount must be greater than zero.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        _, default_bank = server_config.server_settings.get_by_key("default_bank_id")
        bank = await self.bank_repository.get_by_id(int(default_bank.value))
        if not bank:
            raise InvalidDataException("No default bank is configured for this server.")

        if not Helpers.is_in_range(bank.x, bank.y, bank.range, player_profile.player.x, player_profile.player.y):
            raise PermissionDeniedException("You are not close enough to the bank to repay a loan.")

        loan = await self.loan_repository.get_active_by_player_bank(player_profile.player.player_id, bank.bank_id)
        if not loan:
            raise RecordNotFoundException("You do not have an active loan at this bank.")

        payment = min(self.request.amount, loan.balance_remaining)

        async with self.player_balance_repository.transaction():
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - payment
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to make this repayment.")

            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

            loan.balance_remaining -= payment
            if loan.balance_remaining <= 0:
                loan.balance_remaining = 0
                loan.status = 'repaid'

            loan_updated = await self.loan_repository.update(loan)
            if not loan_updated:
                raise UpdateFailedException("Failed to update loan record. Please try again.")

        return RepayLoanCommandResponse(success=True, server_config=server_config, player=player_profile, loan=loan, amount_paid=payment)
