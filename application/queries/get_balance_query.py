from domain import User, GuildConfig
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user

class GetBalanceQueryRequest:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id: int = kwargs.get('guild_id')
        self.user: User = kwargs.get('user')

class GetBalanceQueryResponse:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.success: bool = kwargs.get('success')
        self.guild_config: GuildConfig = kwargs.get('guild_config')
        self.user: User = kwargs.get('user')

class GetBalanceQuery:

    def __init__(self, request: GetBalanceQueryRequest):
        self.request = request
        return

    def execute(self) -> GetBalanceQueryResponse:
        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        return GetBalanceQueryResponse(success=True, guild_config=guild_config, user=user)
