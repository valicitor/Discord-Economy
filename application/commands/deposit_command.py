from dataclasses import dataclass

from domain import User, GuildConfig
from domain import UserNotFoundException, InsufficientFundsException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class DepositCommandRequest:
    guild_id: int
    user: User
    amount: int = None

@dataclass
class DepositCommandResponse:
    success: bool
    guild_config: GuildConfig
    user: User
    amount: int

class DepositCommand:

    def __init__(self, request: DepositCommandRequest):
        self.request = request

        return

    def execute(self) -> DepositCommandResponse:

        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        if self.request.amount is None:
            self.request.amount = user.cash_balance

        # Validate sufficient funds
        user.cash_balance = int(user.cash_balance) - self.request.amount
        if user.cash_balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this deposit.")
        
        user.bank_balance = int(user.bank_balance) + self.request.amount

        success = UserRepository().update(user)

        updated_user = UserRepository().get_by_id(user.guild_id, user.user_id)
        if updated_user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")

        return DepositCommandResponse(success=success, guild_config=guild_config, user=updated_user, amount=self.request.amount)
