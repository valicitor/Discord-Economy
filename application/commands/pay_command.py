import discord
from discord import app_commands
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class PayCommand:

    def __init__(self, interaction: discord.Interaction|None = None):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user_id: str, member_id: str, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:

        await ensure_users(guild_id, [user_id, member_id], interaction=self.interaction)

        user_rec = await self.user_repository.get_by_id(user_id)
        member_rec = await self.user_repository.get_by_id(member_id)

        # Validate sufficient funds
        new_balance = int(user_rec['balance']) - amount
        if new_balance < 0:
            if self.interaction != None and self.interaction.response.is_done():
                await self.interaction.response.send_message(f"Payment failed. Please ensure you have sufficient funds and try again.", ephemeral=True)
            return None
        member_new_balance = int(member_rec['balance']) + amount

        # Update sender balances
        user_rec['balance'] = new_balance
        user_success = await self.user_repository.update(user_rec)

        # Update recipient balances
        member_rec['balance'] = member_new_balance
        member_success = await self.user_repository.update(member_rec)

        return user_success and member_success
