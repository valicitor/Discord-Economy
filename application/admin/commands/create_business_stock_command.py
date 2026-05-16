from attr import dataclass

from infrastructure import BusinessStockRepository, BusinessRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import BusinessStock, CreateFailedException, RecordNotFoundException, DuplicateRecordException

@dataclass
class CreateBusinessStockCommandRequest:
    guild: DiscordGuild
    business_id: int
    base_price: int
    dividend_rate: float = 0.05
    market_points: int = 100

@dataclass
class CreateBusinessStockCommandResponse:
    success: bool
    server_config: ServerConfig
    stock: BusinessStock

class CreateBusinessStockCommand:

    def __init__(self, request: CreateBusinessStockCommandRequest):
        self.request = request

    async def execute(self) -> CreateBusinessStockCommandResponse:
        self.business_stock_repository = await BusinessStockRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        business = await self.business_repository.get_by_id(self.request.business_id)
        if not business:
            raise RecordNotFoundException(f"Business with id '{self.request.business_id}' not found.")

        if await self.business_stock_repository.exists_by_business_id(self.request.business_id):
            raise DuplicateRecordException(f"Business '{business.name}' already has a stock listing.")

        new_stock = BusinessStock(
            business_id=self.request.business_id,
            base_price=self.request.base_price,
            dividend_rate=self.request.dividend_rate,
            market_points=self.request.market_points,
        )
        stock_id = await self.business_stock_repository.insert(new_stock)
        if not stock_id:
            raise CreateFailedException("Failed to create business stock.")

        new_stock.stock_id = stock_id
        return CreateBusinessStockCommandResponse(success=True, server_config=server_config, stock=new_stock)
