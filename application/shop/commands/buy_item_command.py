import json

from attr import dataclass

from infrastructure import ItemRepository, PlayerBalanceRepository, PlayerInventoryRepository, CatalogueRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.helpers.helpers import Helpers
from domain import Item, PlayerInventory, Catalogue, InvalidDataException, RecordNotFoundException, InsufficientFundsException, UpdateFailedException

@dataclass
class BuyItemCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    item_id: int|None
    item_name: str|None

@dataclass
class BuyItemCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    shop_item: Item

class BuyItemCommand:

    def __init__(self, request: BuyItemCommandRequest):
        self.request = request

        return

    async def execute(self) -> BuyItemCommandResponse:
        self.item_repository = await ItemRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.player_inventory_repository = await PlayerInventoryRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()

        if self.request.item_id is None and self.request.item_name is None:
            raise InvalidDataException("Either item_id or item_name must be provided.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)
        
        shop_item = None
        success = False
        async with self.player_inventory_repository.transaction():
            # Check if item exists
            if self.request.item_id is not None:
                shop_item = await self.item_repository.get_by_id(self.request.item_id)
            else:
                shop_item = await self.item_repository.get_by_name(self.request.item_name)
            
            if shop_item is None:
                raise RecordNotFoundException("Item does not exist.")

            # Pay for item
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - shop_item.price
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to complete this purchase.")
            
            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            
            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance


            catalogue_item = await self.catalogue_repository.get_by_id(shop_item.catalogue_id)
            if not catalogue_item:
                raise RecordNotFoundException(f"Catalogue item with id '{catalogue_item.catalogue_id}' not found in guild '{self.request.guild.guild_id}'")
        
            if not catalogue_item.type == "Unit":
                success = await self._add_item_to_inventory(player_profile, catalogue_item)
            else:
                items_to_add = []
                #  { "name": "Clone Trooper",              "type": "Unit",       "description": "Republic soldier, genetically modified and trained",     "metadata": { "starting_gear": { "Species": "Human", "Primary": "DC-15A Blaster Rifle", "Armor": "Phase I Clone Armor" } } },
                if isinstance(catalogue_item.metadata, str):
                    metadata = json.loads(catalogue_item.metadata)
                    # "starting_gear": { "Species": "Droideka", "Primary": "DC-15A Blaster Rifle", "Armor": "Droideka Shield Generator" }
                    starting_gear = metadata.get("starting_gear", {})
                    if not isinstance(starting_gear, dict):
                        raise InvalidDataException("Catalogue item metadata is not valid.")

                    items_to_add = list(starting_gear.values())
                else:
                    raise InvalidDataException("Catalogue item metadata is not valid.")

                for item_name in items_to_add:
                    catalogue_item = await self.catalogue_repository.get_by_name(item_name, server_config.server.server_id)
                    if not catalogue_item:
                        raise RecordNotFoundException(f"Catalogue item with name '{item_name}' not found in guild '{self.request.guild.guild_id}'")#
                    
                    success = await self._add_item_to_inventory(player_profile, catalogue_item)

        return BuyItemCommandResponse(success=success, server_config=server_config, player=player_profile, shop_item=shop_item)

    async def _add_item_to_inventory(self, player_profile: PlayerProfile, catalogue_item: Catalogue) -> bool:
        inventory_item_exists = await self.player_inventory_repository.exists_by_player_catalogue_id(player_id=player_profile.player.player_id, catalogue_id=catalogue_item.catalogue_id)
        if inventory_item_exists:
            inventory_item = await self.player_inventory_repository.get_by_player_catalogue_id(player_profile.player.player_id, catalogue_item.catalogue_id)
            if inventory_item:
                inventory_item.quantity += 1
                success = await self.player_inventory_repository.update(inventory_item)
                return success
            else:
                raise UpdateFailedException("Failed to update player inventory. Please try again.")
        else:
            inventory_instance = PlayerInventory(player_id=player_profile.player.player_id, catalogue_id=catalogue_item.catalogue_id, quantity=1)
            success = await self.player_inventory_repository.insert(inventory_instance)
            if not success:
                raise UpdateFailedException("Failed to update player inventory. Please try again.")
            return success