from domain import User
from domain.exceptions.insufficient_funds_exception import InsufficientFundsException
from domain.exceptions.user_not_found_exception import UserNotFoundException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class PayCommand:

    def __init__(self):
        self.user_repository = UserRepository()

        return

    async def execute(self, guild_id: str, user: User, target: User, amount: int) -> bool|None:

        await ensure_users(guild_id, [user, target])

        user = await self.user_repository.get_by_id(user.user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {guild_id}.")
        
        target = await self.user_repository.get_by_id(target.user_id)
        if target is None:
            raise UserNotFoundException(f"User with ID {target.user_id} not found in guild {guild_id}.")

        # Validate sufficient funds
        new_balance = int(user.cash_balance) - amount
        if new_balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this payment.")
        
        target_new_balance = int(target.cash_balance) + amount

        # Update sender balances
        user.cash_balance = new_balance
        user_success = await self.user_repository.update(user)

        # Update recipient balances
        target.cash_balance = target_new_balance
        target_success = await self.user_repository.update(target)

        return user_success and target_success
