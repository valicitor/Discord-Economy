from domain import User, GuildConfig
from domain import UserNotFoundException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user

class SetBalanceCommandRequest:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id: int = kwargs.get('guild_id')
        self.user: User = kwargs.get('user')
        self.amount: int = kwargs.get('amount')

class SetBalanceCommandResponse:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.success: bool = kwargs.get('success')
        self.guild_config: GuildConfig = kwargs.get('guild_config')
        self.user: User = kwargs.get('user')
        self.amount: int = kwargs.get('amount')

class SetBalanceCommand:

    def __init__(self, request: SetBalanceCommandRequest):
        self.request = request

        return

    def execute(self) -> SetBalanceCommandResponse:

        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        # Update recipient balances
        user.cash_balance = self.request.amount

        success = UserRepository().update(user)
        
        updated_user = UserRepository().get_by_id(user.guild_id, user.user_id)
        if updated_user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")

        return SetBalanceCommandResponse(success=success, guild_config=guild_config, user=updated_user, amount=self.request.amount)
