import discord
from discord import app_commands
from infrastructure import UserRepository, ServerConfigRepository
from application.helpers.ensure_user import ensure_users

class AddBalanceCommand:

    def __init__(self, interaction: discord.Interaction|None = None):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, member_id: str, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:

        await ensure_users(guild_id, [member_id], interaction=self.interaction)

        member_rec = await self.user_repository.get_by_id(member_id)

        # Update recipient balances
        member_rec['balance'] = int(member_rec['balance']) + amount

        member_success = await self.user_repository.update(member_rec)

        return member_success
