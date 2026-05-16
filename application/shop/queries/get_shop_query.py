import math

from attr import dataclass

from infrastructure import ItemRepository, BusinessRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Item

@dataclass
class GetShopQueryRequest:
    guild: DiscordGuild
    user: DiscordUser
    page: int
    sort_by: str
    limit: int

@dataclass
class GetShopQueryResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    shop_items: list[Item]
    page: int
    max_pages: int
    sort_by: str
    limit: int

class GetShopQuery:

    def __init__(self, request: GetShopQueryRequest):
        self.request = request

        return

    async def execute(self) -> GetShopQueryResponse:
        self.item_repository = await ItemRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        businesses = await self.business_repository.get_all_within_range(
            x=player_profile.player.x, y=player_profile.player.y, server_id=server_config.server.server_id
        )
        business_ids = [b.business_id for b in businesses]

        count = await self.item_repository.get_count_in_range(server_config.server.server_id, business_ids)
        if count == 0:
            return GetShopQueryResponse(success=True, server_config=server_config, player=player_profile, shop_items=[], page=1, max_pages=1, sort_by=self.request.sort_by, limit=self.request.limit)

        max_pages = math.ceil(count / self.request.limit)
        if self.request.page > max_pages:
            self.request.page = 1

        shop_items = await self.item_repository.get_shop_items_in_range(server_config.server.server_id, business_ids, self.request.page, self.request.sort_by)

        return GetShopQueryResponse(success=True, server_config=server_config, player=player_profile, shop_items=shop_items, page=self.request.page, max_pages=max_pages, sort_by=self.request.sort_by, limit=self.request.limit)
