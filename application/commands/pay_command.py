from domain import User, GuildConfig
from domain import InsufficientFundsException, UserNotFoundException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_users

class PayCommandRequest:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id: int = kwargs.get('guild_id')
        self.user: User = kwargs.get('user')
        self.target: User = kwargs.get('target')
        self.amount: int = kwargs.get('amount')

class PayCommandResponse:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.success: bool = kwargs.get('success')
        self.guild_config: GuildConfig = kwargs.get('guild_config')
        self.user: User = kwargs.get('user')
        self.target: User = kwargs.get('target')
        self.amount: int = kwargs.get('amount')

class PayCommand:

    def __init__(self, request: PayCommandRequest):
        self.request = request

        return

    def execute(self) -> PayCommandResponse:

        guild_config, (user, target) = ensure_guild_and_users(self.request.guild_id, [self.request.user, self.request.target])

        # Validate sufficient funds
        new_balance = int(user.cash_balance) - self.request.amount
        if new_balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this payment.")
        
        target_new_balance = int(target.cash_balance) + self.request.amount

        # Update sender balances
        user.cash_balance = new_balance
        user_success = UserRepository().update(user)

        # Update recipient balances
        target.cash_balance = target_new_balance
        target_success = UserRepository().update(target)

        updated_user = UserRepository().get_by_id(user.guild_id, user.user_id)
        if updated_user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")
        
        updated_target = UserRepository().get_by_id(target.guild_id, target.user_id)
        if updated_target is None:
            raise UserNotFoundException(f"User with ID {target.user_id} not found in guild {target.guild_id}.")

        return PayCommandResponse(success=user_success and target_success, guild_config=guild_config, user=updated_user, target=updated_target, amount=self.request.amount)
