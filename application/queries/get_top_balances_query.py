import discord
from infrastructure import UserRepository

class GetTopBalancesQuery:

    def __init__(self, interaction: discord.Interaction|None = None):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, limit: int) -> list[dict]|None:
        top_balances = await self.user_repository.get_all(guild_id, limit)

        return top_balances
