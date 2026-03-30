from attr import dataclass

from domain import User, GuildConfig
from domain import UserNotFoundException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class SetBalanceCommandRequest:
    guild_id: int
    user: User
    account_type: str
    amount: int

@dataclass
class SetBalanceCommandResponse:
    success: bool
    guild_config: GuildConfig
    user: User
    account_type: str
    amount: int

class SetBalanceCommand:

    def __init__(self, request: SetBalanceCommandRequest):
        self.request = request

        return

    def execute(self) -> SetBalanceCommandResponse:

        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        # Update recipient balances
        if self.request.account_type == "Cash":
            user.cash_balance = self.request.amount
        elif self.request.account_type == "Bank":
            user.bank_balance = self.request.amount

        success = UserRepository().update(user)
        
        updated_user = UserRepository().get_by_id(user.guild_id, user.user_id)
        if updated_user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")

        return SetBalanceCommandResponse(success=success, guild_config=guild_config, user=updated_user, account_type=self.request.account_type, amount=self.request.amount)
