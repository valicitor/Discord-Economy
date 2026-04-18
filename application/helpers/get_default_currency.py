from domain import RecordNotFoundException
from application import ServerConfig
from infrastructure import (
    CurrencyRepository,
)

async def get_default_currency(server_config: ServerConfig) -> str:
    _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
    if default_currency is None:
        raise RecordNotFoundException(f"Default currency setting not found for server ID {server_config.server.server_id}.")
    
    currency_repository = await CurrencyRepository().get_instance()
    currency = await currency_repository.get_by_id(int(default_currency.value))
    if currency is None:
        raise RecordNotFoundException(f"Default currency with ID {default_currency.value} not found for server ID {server_config.server.server_id}.")
    
    emoji = currency.emoji.strip() if currency.emoji else ""
    symbol = currency.symbol.strip() if currency.symbol else ""

    return(
        emoji.strip()
        if isinstance(emoji, str) and emoji.strip()
        else symbol or ""
    )