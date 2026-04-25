from attr import dataclass
import math

from infrastructure import PlayerRepository

from application import DiscordGuild, ServerConfig, PlayerProfile
from application.helpers.helpers import Helpers

@dataclass
class GetLeaderboardQueryRequest:
    guild: DiscordGuild
    page: int
    sort_by: str
    limit: int

@dataclass
class GetLeaderboardQueryResponse:
    success: bool
    server_config: ServerConfig
    players: list[PlayerProfile]
    page: int
    max_pages: int
    sort_by: str
    limit: int

class GetLeaderboardQuery:

    def __init__(self, request: GetLeaderboardQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetLeaderboardQueryResponse:
        self.player_repository = await PlayerRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        count = await self.player_repository.get_count(server_config.server.server_id)
        if count == 0:
            return GetLeaderboardQueryResponse(success=True, server_config=server_config, players=[], page=1, max_pages=1, limit=self.request.limit, sort_by=self.request.sort_by)

        max_pages = math.ceil(count / self.request.limit)
        if(self.request.page > max_pages):
            self.request.page = 1
        players = await self.player_repository.get_leaderboard(server_config.server.server_id, self.request.page, self.request.sort_by, self.request.limit)

        player_profiles = []
        for idx, player in enumerate(players):
            player_profiles.append(await Helpers.get_player_profile(discord_guild_id=player.discord_guild_id, discord_user_id=player.discord_id))

        return GetLeaderboardQueryResponse(success=True, server_config=server_config, players=player_profiles, page=self.request.page, max_pages=max_pages, limit=self.request.limit, sort_by=self.request.sort_by)