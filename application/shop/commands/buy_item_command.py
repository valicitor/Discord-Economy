import asyncio
import json

from attr import dataclass

from infrastructure import ItemRepository, PlayerBalanceRepository, PlayerInventoryRepository, CatalogueRepository, PlayerUnitRepository, BusinessRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Item, PlayerInventory, PlayerUnit, Catalogue, InvalidDataException, RecordNotFoundException, InsufficientFundsException, UpdateFailedException, PermissionDeniedException

@dataclass
class BuyItemCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    item_id: int|None
    item_name: str|None
    quantity: int|None

@dataclass
class BuyItemCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    shop_item: Item

class BuyItemCommand:

    def __init__(self, request: BuyItemCommandRequest):
        self.request = request

    async def execute(self) -> BuyItemCommandResponse:
        (
            self.item_repository,
            self.player_balance_repository,
            self.player_inventory_repository,
            self.catalogue_repository,
            self.player_unit_repository,
            self.business_repository,
        ) = await asyncio.gather(
            ItemRepository().get_instance(),
            PlayerBalanceRepository().get_instance(),
            PlayerInventoryRepository().get_instance(),
            CatalogueRepository().get_instance(),
            PlayerUnitRepository().get_instance(),
            BusinessRepository().get_instance(),
        )

        if self.request.item_id is None and self.request.item_name is None:
            raise InvalidDataException("Either item_id or item_name must be provided.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        shop_item = None
        success = False
        async with self.player_balance_repository.transaction():
            # Check if shop item exists
            if self.request.item_id is not None:
                shop_item = await self.item_repository.get_by_id(self.request.item_id)
            else:
                shop_item = await self.item_repository.get_by_name(self.request.item_name)

            if shop_item is None:
                raise RecordNotFoundException("Item does not exist.")

            if shop_item.business_id is not None:
                business = await self.business_repository.get_by_id(shop_item.business_id)
                if business and not Helpers.is_in_range(business.x, business.y, business.range, player_profile.player.x, player_profile.player.y):
                    raise PermissionDeniedException("You are not close enough to this shop to buy this item.")

            # Pay for shop item
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - (shop_item.price * self.request.quantity)
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to complete this purchase.")

            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

            # Add shop item to Player inventory
            catalogue_item = await self.catalogue_repository.get_by_id(shop_item.catalogue_id)
            if not catalogue_item:
                raise RecordNotFoundException(f"Catalogue item with id '{shop_item.catalogue_id}' not found in guild '{self.request.guild.guild_id}'")

            if catalogue_item.type == "Vehicle":
                success = await self._add_vehicle_to_player(player_profile, catalogue_item)
            elif catalogue_item.type != "Unit":
                success = await self._add_item_to_inventory(player_profile, catalogue_item, False)
            else:
                if not isinstance(catalogue_item.metadata, str):
                    raise InvalidDataException("Catalogue item metadata is not valid.")

                metadata = json.loads(catalogue_item.metadata)
                starting_gear = metadata.get("starting_gear", {})
                if not isinstance(starting_gear, dict):
                    raise InvalidDataException("Catalogue item metadata is not valid.")

                gear_names = list(starting_gear.values())
                fetched = await asyncio.gather(*[
                    self.catalogue_repository.get_by_name(name, server_config.server.server_id)
                    for name in gear_names
                ])
                related_catalogue_items = []
                for name, related_catalogue_item in zip(gear_names, fetched):
                    if not related_catalogue_item:
                        raise RecordNotFoundException(f"Catalogue item with name '{name}' not found in guild '{self.request.guild.guild_id}'")
                    related_catalogue_items.append(related_catalogue_item)
                    success = await self._add_item_to_inventory(player_profile, related_catalogue_item, True)

                success = await self._add_unit_to_player(player_profile, catalogue_item, related_catalogue_items)

        return BuyItemCommandResponse(success=success, server_config=server_config, player=player_profile, shop_item=shop_item)

    async def _add_item_to_inventory(self, player_profile: PlayerProfile, catalogue_item: Catalogue, is_unit: bool) -> bool:
        status = 'equipped' if is_unit else 'stored'
        inventory_item = await self.player_inventory_repository.get_by_player_catalogue_id(player_profile.player.player_id, catalogue_item.catalogue_id, status=status)
        if inventory_item:
            inventory_item.quantity += self.request.quantity
            success = await self.player_inventory_repository.update(inventory_item)
            return success
        else:
            new_inventory_instance = PlayerInventory(player_id=player_profile.player.player_id, catalogue_id=catalogue_item.catalogue_id, status=status, quantity=self.request.quantity)
            success = await self.player_inventory_repository.insert(new_inventory_instance)
            if not success:
                raise UpdateFailedException("Failed to update player inventory. Please try again.")
            return success

    async def _add_unit_to_player(self, player_profile: PlayerProfile, unit_item: Catalogue, related_items: list[Catalogue]) -> bool:
        unit = await self.player_unit_repository.get_by_name(unit_item.name, player_profile.player.player_id)
        if unit:
            unit.quantity += self.request.quantity
            success = await self.player_unit_repository.update(unit)
            return success

        race = next((obj for obj in related_items if obj.type == "Race"), None)
        if race is None:
            raise InvalidDataException(f"Unit '{unit_item.name}' has no Race in its starting gear.")

        if not isinstance(race.metadata, str):
            raise InvalidDataException("Race catalogue metadata is not valid.")
        try:
            race_metadata = json.loads(race.metadata)
        except json.JSONDecodeError:
            raise InvalidDataException("Race catalogue metadata is not valid JSON.")
        if not isinstance(race_metadata, dict):
            raise InvalidDataException("Race catalogue metadata is not valid.")

        available_slots = race_metadata.get("slots")

        if not isinstance(unit_item.metadata, str):
            raise InvalidDataException("Unit catalogue metadata is not valid.")
        try:
            unit_metadata = json.loads(unit_item.metadata)
        except json.JSONDecodeError:
            raise InvalidDataException("Unit catalogue metadata is not valid JSON.")
        if not isinstance(unit_metadata, dict):
            raise InvalidDataException("Unit catalogue metadata is not valid.")

        assigned_metadata = unit_metadata.get("starting_gear")

        new_unit = PlayerUnit(player_id=player_profile.player.player_id, name=unit_item.name, quantity=self.request.quantity, custom=0, metadata={"slots": available_slots, "assigned": assigned_metadata})
        success = await self.player_unit_repository.insert(new_unit)
        if not success:
            raise UpdateFailedException("Failed to update player units. Please try again.")
        return success

    async def _add_vehicle_to_player(self, player_profile: PlayerProfile, vehicle_item: Catalogue) -> bool:
        vehicle = await self.player_unit_repository.get_by_name(vehicle_item.name, player_profile.player.player_id)
        if vehicle:
            vehicle.quantity += self.request.quantity
            return await self.player_unit_repository.update(vehicle)

        if isinstance(vehicle_item.metadata, str):
            try:
                vehicle_metadata = json.loads(vehicle_item.metadata)
            except json.JSONDecodeError:
                raise InvalidDataException("Vehicle catalogue metadata is not valid JSON.")
        else:
            vehicle_metadata = vehicle_item.metadata or {}

        crew_raw = vehicle_metadata.get("crew", {})
        if isinstance(crew_raw, int):
            crew_slots = {f"Crew {i + 1}": "Unit" for i in range(crew_raw)}
        elif isinstance(crew_raw, dict):
            crew_slots = crew_raw
        else:
            crew_slots = {}
        new_vehicle = PlayerUnit(player_id=player_profile.player.player_id, name=vehicle_item.name, quantity=self.request.quantity, custom=0, metadata={"slots": crew_slots, "assigned": {}})
        success = await self.player_unit_repository.insert(new_vehicle)
        if not success:
            raise UpdateFailedException("Failed to add vehicle. Please try again.")
        return success
