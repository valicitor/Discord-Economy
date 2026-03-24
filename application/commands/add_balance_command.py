import discord
from discord import app_commands
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_user

class AddBalanceCommand:

    def __init__(self, user_repository: UserRepository = UserRepository(), interaction: discord.Interaction|None = None):
        self.user_repository = user_repository
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, member_id: str, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:
        # Ensure the member has an account
        await ensure_user(member_id, guild_id, 0)
        # Fetch recipient data
        member_rec = await self.user_repository.get_by_id(member_id)

        # Validate recipient data
        if member_rec is None:
            if self.interaction != None and self.interaction.response.is_done():
                await self.interaction.response.send_message(f"Payment failed. Please ensure the recipient has an account and try again.", ephemeral=True)
            return None

        member_new_balance = int(member_rec['balance']) + amount

        # Update recipient balances
        member_entity = {
            'id': member_id,
            'guild_id': guild_id,
            'balance': member_new_balance
        }
        member_success = await self.user_repository.update(member_entity)

        return member_success
