from attr import dataclass

from domain import User, GuildConfig
from domain import GuildNotFoundException
from infrastructure import UserRepository, GuildConfigRepository
from application.helpers.ensure_user import ensure_guild
import math

@dataclass
class GetTopBalancesQueryRequest:
    guild_id: int
    page: int
    sort_by: str

@dataclass
class GetTopBalancesQueryResponse:
    success: bool
    guild_config: GuildConfig
    users: list[User]
    page: int
    max_pages: int
    sort_by: str

class GetTopBalancesQuery:

    def __init__(self, request: GetTopBalancesQueryRequest):
        self.request = request
        return

    def execute(self) -> GetTopBalancesQueryResponse:
        ensure_guild(self.request.guild_id)

        guild_config = GuildConfigRepository().get_by_id(self.request.guild_id)
        if guild_config is None:
            raise GuildNotFoundException(f"Failed to ensure guild with ID {self.request.guild_id}.")
        

        max_pages = math.ceil(UserRepository().get_count(guild_config.guild_id) / 10)
        if(self.request.page > max_pages):
            self.request.page = 1
        top_balances = UserRepository().get_leaderboard(guild_config.guild_id, self.request.page, self.request.sort_by)

        return GetTopBalancesQueryResponse(success=True, guild_config=guild_config, users=top_balances, page=self.request.page, max_pages=max_pages, sort_by=self.request.sort_by)
