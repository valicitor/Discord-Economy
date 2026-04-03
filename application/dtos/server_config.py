from domain import Server, ServerSetting
from application import BaseCollection
from dataclasses import dataclass

class ServerSettingsCollection(BaseCollection):
    def __init__(self, settings: list[ServerSetting]):
        super().__init__(settings)

    def get_by_key(self, key: str) -> tuple[int, ServerSetting|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.key == key), (None, None))

@dataclass
class ServerConfig:
    server: Server
    server_settings: ServerSettingsCollection