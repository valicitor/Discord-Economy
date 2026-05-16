from attr import dataclass

from infrastructure import ExchangeRateRepository, PlayerBalanceRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import ExchangeRate, RecordNotFoundException, InvalidDataException, InsufficientFundsException, UpdateFailedException

@dataclass
class ExchangeCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    from_currency_id: int
    to_currency_id: int
    amount: int

@dataclass
class ExchangeCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    exchange_rate: ExchangeRate
    amount_spent: int
    amount_received: int

class ExchangeCommand:

    def __init__(self, request: ExchangeCommandRequest):
        self.request = request

    async def execute(self) -> ExchangeCommandResponse:
        self.exchange_rate_repository = await ExchangeRateRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()

        if self.request.amount <= 0:
            raise InvalidDataException("Exchange amount must be greater than zero.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        exchange_rate = await self.exchange_rate_repository.get_by_pair(
            server_config.server.server_id, self.request.from_currency_id, self.request.to_currency_id
        )
        if not exchange_rate:
            raise RecordNotFoundException("No exchange rate found for this currency pair.")

        amount_received = int(self.request.amount * exchange_rate.rate)
        if amount_received <= 0:
            raise InvalidDataException("Exchange would yield zero. Try a larger amount.")

        async with self.player_balance_repository.transaction():
            i, from_balance = player_profile.balances.get_by_currency_id(self.request.from_currency_id)
            if from_balance is None:
                raise RecordNotFoundException("You do not have a balance for the source currency.")

            from_balance.balance = int(from_balance.balance) - self.request.amount
            if from_balance.balance < 0:
                raise InsufficientFundsException("You do not have enough of that currency to exchange.")

            j, to_balance = player_profile.balances.get_by_currency_id(self.request.to_currency_id)
            if to_balance is None:
                raise RecordNotFoundException("You do not have a balance for the target currency.")
            to_balance.balance = int(to_balance.balance) + amount_received

            from_success = await self.player_balance_repository.update(from_balance)
            if not from_success:
                raise UpdateFailedException("Failed to deduct source currency. Please try again.")

            to_success = await self.player_balance_repository.update(to_balance)
            if not to_success:
                raise UpdateFailedException("Failed to credit target currency. Please try again.")

            from_balance = await self.player_balance_repository.get_by_id(from_balance.balance_id)
            to_balance = await self.player_balance_repository.get_by_id(to_balance.balance_id)
            player_profile.balances[i] = from_balance
            player_profile.balances[j] = to_balance

        return ExchangeCommandResponse(success=True, server_config=server_config, player=player_profile, exchange_rate=exchange_rate, amount_spent=self.request.amount, amount_received=amount_received)
