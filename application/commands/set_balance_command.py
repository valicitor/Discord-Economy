import discord
from discord import app_commands
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_users

class SetBalanceCommand:

    def __init__(self, interaction: discord.Interaction|None = None):
        self.user_repository = UserRepository()
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, member: discord.User | discord.Member, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:

        await ensure_users(guild_id, [{'user_id': member.id, 'username': member.name}], interaction=self.interaction)

        # Update recipient balances
        member_entity = {
            'user_id': member.id,
            'guild_id': guild_id,
            "username": member.name,
            'balance': amount
        }
        member_success = await self.user_repository.update(member_entity)

        return member_success
