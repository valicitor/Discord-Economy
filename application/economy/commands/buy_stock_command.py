import asyncio

from attr import dataclass

from infrastructure import BusinessStockRepository, PlayerStockRepository, PlayerBalanceRepository, BusinessRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import BusinessStock, PlayerStock, RecordNotFoundException, InsufficientFundsException, UpdateFailedException, CreateFailedException

@dataclass
class BuyStockCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    business_id: int
    quantity: int

@dataclass
class BuyStockCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    business_stock: BusinessStock
    quantity: int
    total_cost: int

class BuyStockCommand:

    def __init__(self, request: BuyStockCommandRequest):
        self.request = request

    async def execute(self) -> BuyStockCommandResponse:
        (
            self.business_stock_repository,
            self.player_stock_repository,
            self.player_balance_repository,
            self.business_repository,
        ) = await asyncio.gather(
            BusinessStockRepository().get_instance(),
            PlayerStockRepository().get_instance(),
            PlayerBalanceRepository().get_instance(),
            BusinessRepository().get_instance(),
        )

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        business = await self.business_repository.get_by_id(self.request.business_id)
        if not business:
            raise RecordNotFoundException(f"Business with id '{self.request.business_id}' not found.")

        business_stock = await self.business_stock_repository.get_by_business_id(self.request.business_id)
        if not business_stock:
            raise RecordNotFoundException(f"'{business.name}' does not have publicly traded stock.")

        total_cost = business_stock.current_price * self.request.quantity

        async with self.player_balance_repository.transaction():
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - total_cost
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to buy this stock.")

            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

            existing = await self.player_stock_repository.get_by_player_business(player_profile.player.player_id, self.request.business_id)
            if existing:
                existing.quantity += self.request.quantity
                updated = await self.player_stock_repository.update(existing)
                if not updated:
                    raise UpdateFailedException("Failed to update stock holdings. Please try again.")
            else:
                new_stock = PlayerStock(player_id=player_profile.player.player_id, business_id=self.request.business_id, quantity=self.request.quantity)
                stock_id = await self.player_stock_repository.insert(new_stock)
                if not stock_id:
                    raise CreateFailedException("Failed to record stock purchase. Please try again.")

        return BuyStockCommandResponse(success=True, server_config=server_config, player=player_profile, business_stock=business_stock, quantity=self.request.quantity, total_cost=total_cost)
