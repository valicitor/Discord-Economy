import discord
from infrastructure import UserRepository, ServerConfigRepository
from application.helpers.ensure_user import ensure_user

class GetBalanceQuery:

    def __init__(self, server_config_repository: ServerConfigRepository = ServerConfigRepository(), user_repository: UserRepository = UserRepository(), interaction: discord.Interaction|None = None):
        self.server_config_repository = server_config_repository
        self.user_repository = user_repository
        self.interaction = interaction

        return

    async def execute(self, guild_id: str, user_id: str) -> int|None:
        user = await ensure_user(guild_id, user_id, user_repository=self.user_repository, server_config_repository=self.server_config_repository, interaction=self.interaction)
        return int(user['balance']) # Assuming balance is the third column in the users table
