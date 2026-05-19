import asyncio

from attr import dataclass

from infrastructure import BusinessStockRepository, PlayerStockRepository, PlayerBalanceRepository, BusinessRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import RecordNotFoundException, UpdateFailedException

@dataclass
class PayDividendsCommandRequest:
    guild: DiscordGuild
    business_id: int

@dataclass
class PayDividendsCommandResponse:
    success: bool
    server_config: ServerConfig
    business_name: str
    recipients: int
    total_paid: int

class PayDividendsCommand:

    def __init__(self, request: PayDividendsCommandRequest):
        self.request = request

    async def execute(self) -> PayDividendsCommandResponse:
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

        business = await self.business_repository.get_by_id(self.request.business_id)
        if not business:
            raise RecordNotFoundException(f"Business with id '{self.request.business_id}' not found.")

        business_stock = await self.business_stock_repository.get_by_business_id(self.request.business_id)
        if not business_stock:
            raise RecordNotFoundException(f"'{business.name}' does not have publicly traded stock.")

        player_stocks = await self.player_stock_repository.get_all_by_business_id(self.request.business_id)

        _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
        default_currency_id = int(default_currency.value)

        # Bulk-load balances for all shareholders at once
        player_ids = list({ps.player_id for ps in player_stocks})
        all_balances = []
        for pid in player_ids:
            all_balances.extend(await self.player_balance_repository.get_all(player_id=pid))
        balances_by_player = {
            b.player_id: b for b in all_balances if b.currency_id == default_currency_id
        }

        total_paid = 0
        recipients = 0
        for ps in player_stocks:
            payout = int(business_stock.current_price * business_stock.dividend_rate * ps.quantity)
            if payout <= 0:
                continue

            balance = balances_by_player.get(ps.player_id)
            if not balance:
                continue

            balance.balance = int(balance.balance) + payout
            success = await self.player_balance_repository.update(balance)
            if not success:
                raise UpdateFailedException(f"Failed to pay dividend to player {ps.player_id}.")

            total_paid += payout
            recipients += 1

        return PayDividendsCommandResponse(success=True, server_config=server_config, business_name=business.name, recipients=recipients, total_paid=total_paid)
