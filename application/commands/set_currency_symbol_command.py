import re

from attr import dataclass

from infrastructure import CurrencyRepository
from application import DiscordGuild, ServerConfig

from domain import Currency

from application.helpers.ensure_user import ensure_guild

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

    def execute(self) -> SetCurrencySymbolCommandResponse:
        server_config = ensure_guild(self.request.guild)

        default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)
        currency = CurrencyRepository().get_by_id(int(default_currency_id))

        symbol = (self.request.currency_symbol or "").strip()

        is_custom = any(ord(char) >= 0x1F300 for char in symbol)
        is_unicode = bool(re.compile(r"^<a?:\w+:\d+>$").match(symbol))

        if is_custom or is_unicode:
            currency.emoji = symbol
            currency.symbol = ""
        else:
            currency.emoji = ""
            currency.symbol = symbol[:10]

        success = CurrencyRepository().update(currency)
        if not success:
            raise Exception("Failed to update currency. Please try again.")

        return SetCurrencySymbolCommandResponse(success=success, server_config=server_config, currency=currency)
