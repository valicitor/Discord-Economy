import discord
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_user

class GetBalanceQuery:

    def __init__(self, user_repository: UserRepository = UserRepository(), interaction: discord.Interaction|None = None):
        self.user_repository = user_repository
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user_id: str) -> int|None:
        await ensure_user(user_id, guild_id, 0)
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            if self.interaction != None and self.interaction.response.is_done():
                await self.interaction.response.send_message(f"Payment failed. Please ensure you have an account and try again.", ephemeral=True)
            return None

        return int(user['balance']) # Assuming balance is the third column in the users table
