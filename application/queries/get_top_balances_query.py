from domain import User
from infrastructure import UserRepository

class GetTopBalancesQuery:

    def __init__(self):
        self.user_repository = UserRepository()

        return

    async def execute(self, guild_id: str, page: int, sort_by: str) -> list[User]|None:
        top_balances = await self.user_repository.get_leaderboard(guild_id, page, sort_by)

        return top_balances
