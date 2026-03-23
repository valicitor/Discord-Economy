import discord
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_user

class GetBalanceQuery:

    def __init__(self, interaction: discord.Interaction):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user_id: str) -> int|None:
        await ensure_user(user_id, guild_id, 0)
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            await self.interaction.response.send_message(f"Payment failed. Please ensure you have an account and try again.", ephemeral=True)
            return None

        return int(user[2]) # Assuming balance is the third column in the users table
