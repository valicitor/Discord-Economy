import discord
from discord import app_commands
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_user

class PayCommand:

    def __init__(self, interaction: discord.Interaction):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user_id: str, member_id: str, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:
        await ensure_user(user_id, guild_id, 0)
        # Fetch sender data
        user_rec = await self.user_repository.get_by_id(user_id)

        # Ensure the member has an account
        await ensure_user(member_id, guild_id, 0)
        # Fetch recipient data
        member_rec = await self.user_repository.get_by_id(member_id)

        # Validate sender and recipient data
        if user_rec is None:
            await self.interaction.response.send_message(f"Payment failed. Please ensure you have an account and try again.", ephemeral=True)
            return None
        if member_rec is None:
            await self.interaction.response.send_message(f"Payment failed. Please ensure the recipient has an account and try again.", ephemeral=True)
            return None

        # Validate sufficient funds
        new_balance = int(user_rec[2]) - amount
        if new_balance < 0:
            await self.interaction.response.send_message(f"Payment failed. Please ensure you have sufficient funds and try again.", ephemeral=True)
            return None
        member_new_balance = int(member_rec[2]) + amount

        # Update sender balances
        user_entity = {
            'id': user_id,
            'guild_id': guild_id,
            'balance': new_balance
        }
        user_success = await self.user_repository.update(user_entity)

        # Update recipient balances
        member_entity = {
            'id': member_id,
            'guild_id': guild_id,
            'balance': member_new_balance
        }
        member_success = await self.user_repository.update(member_entity)

        return user_success and member_success
