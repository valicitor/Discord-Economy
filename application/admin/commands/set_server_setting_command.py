from attr import dataclass

from infrastructure import ServerSettingRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import ServerSetting, UpdateFailedException, CreateFailedException

@dataclass
class SetServerSettingCommandRequest:
    guild: DiscordGuild
    key: str
    value: str

@dataclass
class SetServerSettingCommandResponse:
    success: bool
    server_config: ServerConfig
    setting: ServerSetting

class SetServerSettingCommand:

    def __init__(self, request: SetServerSettingCommandRequest):
        self.request = request

    async def execute(self) -> SetServerSettingCommandResponse:
        self.server_setting_repository = await ServerSettingRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        i, existing = server_config.server_settings.get_by_key(self.request.key)

        if existing:
            existing.value = self.request.value
            success = await self.server_setting_repository.update(existing)
            if not success:
                raise UpdateFailedException(f"Failed to update setting '{self.request.key}'.")
            server_config.server_settings[i] = existing
            return SetServerSettingCommandResponse(success=True, server_config=server_config, setting=existing)

        new_setting = ServerSetting(
            server_id=server_config.server.server_id,
            key=self.request.key,
            value=self.request.value,
        )
        setting_id = await self.server_setting_repository.insert(new_setting)
        if not setting_id:
            raise CreateFailedException(f"Failed to create setting '{self.request.key}'.")

        new_setting.setting_id = setting_id
        return SetServerSettingCommandResponse(success=True, server_config=server_config, setting=new_setting)
