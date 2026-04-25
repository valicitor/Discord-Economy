from domain import Server, ServerSetting
from application import BaseCollection
from dataclasses import dataclass
from infrastructure import CurrencyRepository, ServerSettingRepository
from domain import RecordNotFoundException

class ServerSettingsCollection(BaseCollection):
    def __init__(self, settings: list[ServerSetting]):
        super().__init__(settings)

    def get_by_key(self, key: str) -> tuple[int, ServerSetting|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.key == key), (None, None))

@dataclass
class ServerConfig:
    server: Server
    server_settings: ServerSettingsCollection

    async def get_default_currency(self) -> str:
        _, default_currency = self.server_settings.get_by_key("default_currency_id")
        if default_currency is None:
            raise RecordNotFoundException(f"Default currency setting not found for server ID {self.server.server_id}.")
        
        currency_repository = await CurrencyRepository().get_instance()
        currency = await currency_repository.get_by_id(int(default_currency.value))
        if currency is None:
            raise RecordNotFoundException(f"Default currency with ID {default_currency.value} not found for server ID {self.server.server_id}.")
        
        emoji = currency.emoji.strip() if currency.emoji else ""
        symbol = currency.symbol.strip() if currency.symbol else ""

        return(
            emoji.strip()
            if isinstance(emoji, str) and emoji.strip()
            else symbol or ""
        )