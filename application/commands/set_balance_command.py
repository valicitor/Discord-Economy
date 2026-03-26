from domain import User
from domain.exceptions.user_not_found_exception import UserNotFoundException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class SetBalanceCommand:

    def __init__(self):
        self.user_repository = UserRepository()

        return

    async def execute(self, guild_id: str, user: User, amount: int) -> bool|None:

        await ensure_users(guild_id, [ user ])

        user = await self.user_repository.get_by_id(user.user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {guild_id}.")

        # Update recipient balances
        user.cash_balance = amount

        return await self.user_repository.update(user)
