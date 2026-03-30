from domain import (
    Server, 
    ServerSetting,
)
from dataclasses import dataclass

@dataclass
class ServerConfig:
    server: Server
    server_settings: list[ServerSetting]