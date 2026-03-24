import discord
from discord import app_commands
from infrastructure import UserRepository, ServerConfigRepository
from application.helpers.ensure_user import ensure_user

class AddBalanceCommand:

    def __init__(self, server_config_repository: ServerConfigRepository = ServerConfigRepository(), user_repository: UserRepository = UserRepository(), interaction: discord.Interaction|None = None):
        self.server_config_repository = server_config_repository
        self.user_repository = user_repository
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, member_id: str, amount: app_commands.Range[int, 1, 100000000]) -> bool|None:

        member_rec = await ensure_user(guild_id, member_id, user_repository=self.user_repository, server_config_repository=self.server_config_repository, interaction=self.interaction)

        member_new_balance = int(member_rec['balance']) + amount

        # Update recipient balances
        member_entity = {
            'id': member_id,
            'guild_id': guild_id,
            'balance': member_new_balance
        }
        member_success = await self.user_repository.update(member_entity)

        return member_success
