import discord
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class GetBalanceQuery:

    def __init__(self, interaction: discord.Interaction|None = None):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user: discord.User | discord.Member) -> int|None:
        await ensure_users(guild_id, [{'user_id': user.id, 'username': user.name}], interaction=self.interaction)
        user_rec = await self.user_repository.get_by_id(user.id)

        return int(user_rec['balance'])
