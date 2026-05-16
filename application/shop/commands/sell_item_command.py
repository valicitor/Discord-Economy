from attr import dataclass

from infrastructure import ItemRepository, PlayerBalanceRepository, PlayerInventoryRepository, CatalogueRepository, PlayerUnitRepository, BusinessRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Item, PlayerInventory, InvalidDataException, RecordNotFoundException, UpdateFailedException, PermissionDeniedException

_SELL_RATE = 0.5

@dataclass
class SellItemCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    item_id: int | None
    item_name: str | None
    quantity: int

@dataclass
class SellItemCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    shop_item: Item
    sell_amount: int

class SellItemCommand:

    def __init__(self, request: SellItemCommandRequest):
        self.request = request

    async def execute(self) -> SellItemCommandResponse:
        self.item_repository = await ItemRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.player_inventory_repository = await PlayerInventoryRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()
        self.player_unit_repository = await PlayerUnitRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()

        if self.request.item_id is None and self.request.item_name is None:
            raise InvalidDataException("Either item_id or item_name must be provided.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        shop_item = None
        sell_amount = 0
        success = False

        async with self.player_balance_repository.transaction():
            if self.request.item_id is not None:
                shop_item = await self.item_repository.get_by_id(self.request.item_id)
            else:
                shop_item = await self.item_repository.get_by_name(self.request.item_name)

            if shop_item is None:
                raise RecordNotFoundException("Item does not exist.")

            if not shop_item.sellable:
                raise InvalidDataException(f"'{shop_item.name}' cannot be sold.")

            if shop_item.business_id is not None:
                business = await self.business_repository.get_by_id(shop_item.business_id)
                if business and not Helpers.is_in_range(business.x, business.y, business.range, player_profile.player.x, player_profile.player.y):
                    raise PermissionDeniedException("You are not close enough to this shop to sell this item.")

            catalogue_item = await self.catalogue_repository.get_by_id(shop_item.catalogue_id)
            if not catalogue_item:
                raise RecordNotFoundException(f"Catalogue entry for '{shop_item.name}' not found.")

            if catalogue_item.type == "Unit":
                success = await self._sell_unit(player_profile, catalogue_item)
            else:
                success = await self._sell_inventory_item(player_profile, catalogue_item)

            sell_amount = int(shop_item.price * _SELL_RATE) * self.request.quantity

            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance += sell_amount
            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

        return SellItemCommandResponse(
            success=success,
            server_config=server_config,
            player=player_profile,
            shop_item=shop_item,
            sell_amount=sell_amount
        )

    async def _sell_inventory_item(self, player_profile: PlayerProfile, catalogue_item) -> bool:
        inventory_item = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='stored'
        )
        if not inventory_item or inventory_item.quantity < self.request.quantity:
            raise InvalidDataException(f"You don't have {self.request.quantity}x '{catalogue_item.name}' to sell.")

        inventory_item.quantity -= self.request.quantity
        if inventory_item.quantity == 0:
            return await self.player_inventory_repository.delete(inventory_item)
        return await self.player_inventory_repository.update(inventory_item)

    async def _sell_unit(self, player_profile: PlayerProfile, catalogue_item) -> bool:
        unit = await self.player_unit_repository.get_by_name(catalogue_item.name, player_profile.player.player_id)
        if not unit or unit.quantity < self.request.quantity:
            raise InvalidDataException(f"You don't have {self.request.quantity}x '{catalogue_item.name}' to sell.")

        unit.quantity -= self.request.quantity
        if unit.quantity == 0:
            return await self.player_unit_repository.delete(unit)
        return await self.player_unit_repository.update(unit)
