from attr import dataclass

from infrastructure import PlayerStockRepository, BusinessStockRepository, BusinessRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import PlayerStock, BusinessStock, Business

@dataclass
class GetStocksQueryRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class GetStocksQueryResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    holdings: list[tuple[PlayerStock, BusinessStock, Business]]

class GetStocksQuery:

    def __init__(self, request: GetStocksQueryRequest):
        self.request = request

    async def execute(self) -> GetStocksQueryResponse:
        self.player_stock_repository = await PlayerStockRepository().get_instance()
        self.business_stock_repository = await BusinessStockRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        player_stocks = await self.player_stock_repository.get_all_by_player_id(player_profile.player.player_id)

        holdings = []
        for ps in player_stocks:
            business_stock = await self.business_stock_repository.get_by_business_id(ps.business_id)
            business = await self.business_repository.get_by_id(ps.business_id)
            if business_stock and business:
                holdings.append((ps, business_stock, business))

        return GetStocksQueryResponse(success=True, server_config=server_config, player=player_profile, holdings=holdings)
