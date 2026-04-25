import re

from attr import dataclass

from domain import UpdateFailedException
from infrastructure import CurrencyRepository
from application import DiscordGuild, ServerConfig

from domain import Currency, RecordNotFoundException

from application.helpers.helpers import Helpers

@dataclass
class SetCurrencySymbolCommandRequest:
    guild: DiscordGuild
    currency_symbol: str

@dataclass
class SetCurrencySymbolCommandResponse:
    success: bool
    server_config: ServerConfig
    currency: Currency

class SetCurrencySymbolCommand:

    def __init__(self, request: SetCurrencySymbolCommandRequest):
        self.request = request
        return

    async def execute(self) -> SetCurrencySymbolCommandResponse:
        self.currency_repository = await CurrencyRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        
        _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
        currency = await self.currency_repository.get_by_id(int(default_currency.value))

        symbol = (self.request.currency_symbol or "").strip()

        is_custom = any(ord(char) >= 0x1F300 for char in symbol)
        is_unicode = bool(re.compile(r"^<a?:\w+:\d+>$").match(symbol))

        if is_custom or is_unicode:
            currency.emoji = symbol
            currency.symbol = ""
        else:
            currency.emoji = ""
            currency.symbol = symbol[:10]

        success = await self.currency_repository.update(currency)
        if not success:
            raise UpdateFailedException("Failed to update currency. Please try again.")

        return SetCurrencySymbolCommandResponse(success=success, server_config=server_config, currency=currency)
