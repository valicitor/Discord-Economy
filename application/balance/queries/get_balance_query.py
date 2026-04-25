from attr import dataclass

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.helpers.helpers import Helpers

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
        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        return GetBalanceQueryResponse(success=True, server_config=server_config, player=player_profile)
