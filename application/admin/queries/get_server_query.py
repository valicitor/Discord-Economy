from attr import dataclass

from application import ServerConfig, ServerSettingsCollection
from domain import RecordNotFoundException
from infrastructure import ServerRepository, ServerSettingRepository

@dataclass
class GetServerQueryRequest:
    discord_guild_id: int

@dataclass
class GetServerQueryResponse:
    success: bool
    server_config: ServerConfig

class GetServerQuery:

    def __init__(self, request: GetServerQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetServerQueryResponse:
        server_repo = await ServerRepository().get_instance()
        server_setting_repo = await ServerSettingRepository().get_instance()
        
        server_exists = await server_repo.exists_by_guild_id(self.request.discord_guild_id)
        if not server_exists:
            raise RecordNotFoundException(f"Server not found for guild ID {self.request.discord_guild_id}.")
        
        server = await server_repo.get_by_guild_id(self.request.discord_guild_id)
        if server is None:
            raise RecordNotFoundException(f"Failed to fetch a server with guild ID {self.request.discord_guild_id}.")
        
        server_settings = await server_setting_repo.get_all_by_server_id(server.server_id)
        if server_settings is None:
            raise RecordNotFoundException(f"Failed to fetch a server settings for guild ID {self.request.discord_guild_id}.")

        return GetServerQueryResponse(
            success=True, 
                server_config=ServerConfig(
                server, 
                ServerSettingsCollection(server_settings)
            )
        )
