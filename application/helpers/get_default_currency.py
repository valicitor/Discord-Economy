from domain import RecordNotFoundException
from application import ServerConfig
from infrastructure import (
    CurrencyRepository,
)

def get_default_currenncy(server_config: ServerConfig) -> str:
    default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)
    currency = CurrencyRepository().get_by_id(int(default_currency_id))
    if currency is None:
        raise RecordNotFoundException(f"Default currency with ID {default_currency_id} not found for server ID {server_config.server.server_id}.")
    
    emoji = currency.emoji.strip() if currency.emoji else ""
    symbol = currency.symbol.strip() if currency.symbol else ""

    return(
        emoji.strip()
        if isinstance(emoji, str) and emoji.strip()
        else symbol or ""
    )