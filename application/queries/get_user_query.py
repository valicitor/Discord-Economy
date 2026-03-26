from domain import User
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class GetUserQuery:

    def __init__(self):
        self.user_repository = UserRepository()

        return

    async def execute(self, guild_id: str, user: User) -> User|None:
        await ensure_users(guild_id, [user])
        user = await self.user_repository.get_by_id(user.user_id)

        if user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {guild_id}.")

        return user
