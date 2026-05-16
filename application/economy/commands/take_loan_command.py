from attr import dataclass

from infrastructure import LoanRepository, PlayerBalanceRepository, BankRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Loan, PermissionDeniedException, InvalidDataException, CreateFailedException, UpdateFailedException

@dataclass
class TakeLoanCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    amount: int

@dataclass
class TakeLoanCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    loan: Loan

class TakeLoanCommand:

    def __init__(self, request: TakeLoanCommandRequest):
        self.request = request

    async def execute(self) -> TakeLoanCommandResponse:
        self.loan_repository = await LoanRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.bank_repository = await BankRepository().get_instance()

        if self.request.amount <= 0:
            raise InvalidDataException("Loan amount must be greater than zero.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        _, default_bank = server_config.server_settings.get_by_key("default_bank_id")
        bank = await self.bank_repository.get_by_id(int(default_bank.value))
        if not bank:
            raise InvalidDataException("No default bank is configured for this server.")

        if not Helpers.is_in_range(bank.x, bank.y, bank.range, player_profile.player.x, player_profile.player.y):
            raise PermissionDeniedException("You are not close enough to the bank to take a loan.")

        existing_loan = await self.loan_repository.get_active_by_player_bank(player_profile.player.player_id, bank.bank_id)
        if existing_loan:
            raise InvalidDataException("You already have an active loan. Repay it before taking another.")

        loan = Loan(
            player_id=player_profile.player.player_id,
            bank_id=bank.bank_id,
            principal=self.request.amount,
            interest_rate=bank.interest_rate,
            balance_remaining=int(self.request.amount * (1 + bank.interest_rate)),
            status='active'
        )

        async with self.player_balance_repository.transaction():
            loan_id = await self.loan_repository.insert(loan)
            if not loan_id:
                raise CreateFailedException("Failed to create loan. Please try again.")
            loan.loan_id = loan_id

            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
            balance.balance = int(balance.balance) + self.request.amount

            success = await self.player_balance_repository.update(balance)
            if not success:
                raise UpdateFailedException("Failed to credit loan funds. Please try again.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

        return TakeLoanCommandResponse(success=True, server_config=server_config, player=player_profile, loan=loan)
