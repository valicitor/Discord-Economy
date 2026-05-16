from attr import dataclass

from infrastructure import ExchangeRateRepository, CurrencyRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import ExchangeRate, UpdateFailedException, RecordNotFoundException

@dataclass
class SetExchangeRateCommandRequest:
    guild: DiscordGuild
    from_currency_id: int
    to_currency_id: int
    rate: float

@dataclass
class SetExchangeRateCommandResponse:
    success: bool
    server_config: ServerConfig
    exchange_rate: ExchangeRate

class SetExchangeRateCommand:

    def __init__(self, request: SetExchangeRateCommandRequest):
        self.request = request

    async def execute(self) -> SetExchangeRateCommandResponse:
        self.exchange_rate_repository = await ExchangeRateRepository().get_instance()
        self.currency_repository = await CurrencyRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        from_currency = await self.currency_repository.get_by_id(self.request.from_currency_id)
        if not from_currency:
            raise RecordNotFoundException(f"Currency with id '{self.request.from_currency_id}' not found.")

        to_currency = await self.currency_repository.get_by_id(self.request.to_currency_id)
        if not to_currency:
            raise RecordNotFoundException(f"Currency with id '{self.request.to_currency_id}' not found.")

        existing = await self.exchange_rate_repository.get_by_pair(
            server_config.server.server_id,
            self.request.from_currency_id,
            self.request.to_currency_id,
        )

        if existing:
            existing.rate = self.request.rate
            success = await self.exchange_rate_repository.update(existing)
            if not success:
                raise UpdateFailedException("Failed to update exchange rate.")
            return SetExchangeRateCommandResponse(success=True, server_config=server_config, exchange_rate=existing)

        new_rate = ExchangeRate(
            server_id=server_config.server.server_id,
            from_currency_id=self.request.from_currency_id,
            to_currency_id=self.request.to_currency_id,
            rate=self.request.rate,
        )
        rate_id = await self.exchange_rate_repository.insert(new_rate)
        if not rate_id:
            raise UpdateFailedException("Failed to create exchange rate.")

        new_rate.rate_id = rate_id
        return SetExchangeRateCommandResponse(success=True, server_config=server_config, exchange_rate=new_rate)
