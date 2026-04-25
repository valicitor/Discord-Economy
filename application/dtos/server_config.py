from domain import Server, ServerSetting
from application import BaseCollection
from dataclasses import dataclass
from infrastructure import CurrencyRepository, BankRepository, FactionRepository
from domain import Currency, Bank, Faction, RecordNotFoundException

class ServerSettingsCollection(BaseCollection):
    def __init__(self, settings: list[ServerSetting]):
        super().__init__(settings)

    def get_by_key(self, key: str) -> tuple[int, ServerSetting|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.key == key), (None, None))

@dataclass
class ServerConfig:
    server: Server
    server_settings: ServerSettingsCollection

    async def get_default_currency_symbol(self) -> str:
        currency = await self.get_default_currency()
        
        emoji = currency.emoji.strip() if currency.emoji else ""
        symbol = currency.symbol.strip() if currency.symbol else ""

        return(
            emoji.strip()
            if isinstance(emoji, str) and emoji.strip()
            else symbol or ""
        )

    async def get_default_currency(self) -> Currency:
        _, default_currency = self.server_settings.get_by_key("default_currency_id")
        if default_currency is None:
            raise RecordNotFoundException(f"Default currency setting not found for server ID {self.server.server_id}.")
        
        currency_repository = await CurrencyRepository().get_instance()
        currency = await currency_repository.get_by_id(int(default_currency.value))
        if currency is None:
            raise RecordNotFoundException(f"Default currency with ID {default_currency.value} not found for server ID {self.server.server_id}.")

        return currency

    async def get_default_bank(self) -> Bank:
        _, default_bank = self.server_settings.get_by_key("default_bank_id")
        if default_bank is None:
            raise RecordNotFoundException(f"Default bank setting not found for server ID {self.server.server_id}.")
        
        bank_repository = await BankRepository().get_instance()
        bank = await bank_repository.get_by_id(int(default_bank.value))
        if bank is None:
            raise RecordNotFoundException(f"Default bank with ID {default_bank.value} not found for server ID {self.server.server_id}.")

        return bank

    async def get_default_faction(self) -> Faction:
        _, default_faction = self.server_settings.get_by_key("default_faction_id")
        if default_faction is None:
            raise RecordNotFoundException(f"Default faction setting not found for server ID {self.server.server_id}.")
        
        faction_repository = await FactionRepository().get_instance()
        faction = await faction_repository.get_by_id(int(default_faction.value))
        if faction is None:
            raise RecordNotFoundException(f"Default faction with ID {default_faction.value} not found for server ID {self.server.server_id}.")
        
        return faction