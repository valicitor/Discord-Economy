from attr import dataclass

from domain import User, GuildConfig
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user

@dataclass
class GetBalanceQueryRequest:
    guild_id: int
    user: User

@dataclass
class GetBalanceQueryResponse:
    success: bool
    guild_config: GuildConfig
    user: User

class GetBalanceQuery:

    def __init__(self, request: GetBalanceQueryRequest):
        self.request = request
        return

    def execute(self) -> GetBalanceQueryResponse:
        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        return GetBalanceQueryResponse(success=True, guild_config=guild_config, user=user)
