from attr import dataclass

from infrastructure import PlayerRepository
from application import DiscordGuild, ServerConfig, PlayerProfile
from application.helpers.ensure_user import ensure_guild

import math

@dataclass
class GetTopBalancesQueryRequest:
    guild: DiscordGuild
    page: int
    sort_by: str

@dataclass
class GetTopBalancesQueryResponse:
    success: bool
    server_config: ServerConfig
    players: list[PlayerProfile]
    page: int
    max_pages: int
    sort_by: str

class GetTopBalancesQuery:

    def __init__(self, request: GetTopBalancesQueryRequest):
        self.request = request
        return

    def execute(self) -> GetTopBalancesQueryResponse:
        server_config = ensure_guild(self.request.guild)

        max_pages = math.ceil(PlayerRepository().get_count(server_config.server_id) / 10)
        if(self.request.page > max_pages):
            self.request.page = 1
        top_balances = PlayerRepository().get_leaderboard(server_config.server_id, self.request.page, self.request.sort_by)

        return GetTopBalancesQueryResponse(success=True, server_config=server_config, players=top_balances, page=self.request.page, max_pages=max_pages, sort_by=self.request.sort_by)
