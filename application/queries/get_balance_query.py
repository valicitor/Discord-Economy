from attr import dataclass

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class GetBalanceQueryRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class GetBalanceQueryResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile

class GetBalanceQuery:

    def __init__(self, request: GetBalanceQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetBalanceQueryResponse:
        server_config, player = await ensure_guild_and_user(self.request.guild, self.request.user)

        return GetBalanceQueryResponse(success=True, server_config=server_config, player=player)
