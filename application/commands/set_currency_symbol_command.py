import re

from attr import dataclass

from domain import GuildConfig
from domain import GuildNotFoundException
from infrastructure import GuildConfigRepository
from application.helpers.ensure_user import ensure_guild

CUSTOM_EMOJI_PATTERN = re.compile(r"^<a?:\w+:\d+>$")

@dataclass
class SetCurrencySymbolCommandRequest:
    guild_id: int
    currency_symbol: str

@dataclass
class SetCurrencySymbolCommandResponse:
    success: bool
    guild_config: GuildConfig
    currency_symbol: str

class SetCurrencySymbolCommand:

    def __init__(self, request: SetCurrencySymbolCommandRequest):
        self.request = request
        return

    def _is_custom_emoji(self, value: str) -> bool:
        return bool(CUSTOM_EMOJI_PATTERN.match(value))

    def _is_unicode_emoji(self, value: str) -> bool:
        # Minimal but safer heuristic:
        return any(ord(char) >= 0x1F300 for char in value)

    def execute(self) -> SetCurrencySymbolCommandResponse:

        guild_config = ensure_guild(self.request.guild_id)

        symbol = (self.request.currency_symbol or "").strip()

        is_custom = self._is_custom_emoji(symbol)
        is_unicode = self._is_unicode_emoji(symbol)

        if is_custom or is_unicode:
            guild_config.currency_emoji = symbol
            guild_config.currency_symbol = ""
        else:
            guild_config.currency_emoji = ""
            guild_config.currency_symbol = symbol[:10]

        success = GuildConfigRepository().update(guild_config)

        updated_guild_config = GuildConfigRepository().get_by_id(guild_config.guild_id)
        if updated_guild_config is None:
            raise GuildNotFoundException(f"Guild with ID {guild_config.guild_id} not found.")

        return SetCurrencySymbolCommandResponse(
            success=success,
            guild_config=updated_guild_config,
            currency_symbol=symbol
        )
