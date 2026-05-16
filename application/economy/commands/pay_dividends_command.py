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
        self.business_stock_repository = await BusinessStockRepository().get_instance()
        self.player_stock_repository = await PlayerStockRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        business = await self.business_repository.get_by_id(self.request.business_id)
        if not business:
            raise RecordNotFoundException(f"Business with id '{self.request.business_id}' not found.")

        business_stock = await self.business_stock_repository.get_by_business_id(self.request.business_id)
        if not business_stock:
            raise RecordNotFoundException(f"'{business.name}' does not have publicly traded stock.")

        player_stocks = await self.player_stock_repository.get_all_by_business_id(self.request.business_id)

        total_paid = 0
        recipients = 0
        for ps in player_stocks:
            payout = int(business_stock.current_price * business_stock.dividend_rate * ps.quantity)
            if payout <= 0:
                continue

            balance_rows = await self.player_balance_repository.get_all(player_id=ps.player_id)
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            balance = next((b for b in balance_rows if b.currency_id == int(default_currency.value)), None)
            if not balance:
                continue

            balance.balance = int(balance.balance) + payout
            success = await self.player_balance_repository.update(balance)
            if not success:
                raise UpdateFailedException(f"Failed to pay dividend to player {ps.player_id}.")

            total_paid += payout
            recipients += 1

        return PayDividendsCommandResponse(success=True, server_config=server_config, business_name=business.name, recipients=recipients, total_paid=total_paid)
