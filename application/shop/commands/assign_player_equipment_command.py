from attr import dataclass

from infrastructure import ItemRepository, PlayerInventoryRepository, CatalogueRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Item, PlayerInventory, InvalidDataException, RecordNotFoundException, UpdateFailedException

@dataclass
class AssignPlayerEquipmentCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    item_name: str
    equip: bool  # True = equip to character, False = unequip

@dataclass
class AssignPlayerEquipmentCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    item: Item
    equipped: bool

class AssignPlayerEquipmentCommand:

    def __init__(self, request: AssignPlayerEquipmentCommandRequest):
        self.request = request

    async def execute(self) -> AssignPlayerEquipmentCommandResponse:
        self.item_repository = await ItemRepository().get_instance()
        self.player_inventory_repository = await PlayerInventoryRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        async with self.player_inventory_repository.transaction():
            shop_item = await self.item_repository.get_by_name(self.request.item_name)
            if not shop_item:
                raise RecordNotFoundException(f"Item '{self.request.item_name}' not found.")

            catalogue_item = await self.catalogue_repository.get_by_id(shop_item.catalogue_id)
            if not catalogue_item:
                raise RecordNotFoundException(f"Catalogue entry for '{self.request.item_name}' not found.")

            if self.request.equip:
                await self._equip(player_profile, catalogue_item)
            else:
                await self._unequip(player_profile, catalogue_item)

        return AssignPlayerEquipmentCommandResponse(
            success=True,
            server_config=server_config,
            player=player_profile,
            item=shop_item,
            equipped=self.request.equip
        )

    async def _equip(self, player_profile: PlayerProfile, catalogue_item) -> None:
        stored = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='stored'
        )
        if not stored or stored.quantity < 1:
            raise InvalidDataException(f"You don't have '{catalogue_item.name}' in your inventory.")

        stored.quantity -= 1
        if stored.quantity == 0:
            await self.player_inventory_repository.delete(stored)
        else:
            await self.player_inventory_repository.update(stored)

        character_slot = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='character'
        )
        if character_slot:
            character_slot.quantity += 1
            await self.player_inventory_repository.update(character_slot)
        else:
            await self.player_inventory_repository.insert(PlayerInventory(
                player_id=player_profile.player.player_id,
                catalogue_id=catalogue_item.catalogue_id,
                status='character',
                quantity=1
            ))

    async def _unequip(self, player_profile: PlayerProfile, catalogue_item) -> None:
        character_slot = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='character'
        )
        if not character_slot or character_slot.quantity < 1:
            raise InvalidDataException(f"'{catalogue_item.name}' is not equipped on your character.")

        character_slot.quantity -= 1
        if character_slot.quantity == 0:
            await self.player_inventory_repository.delete(character_slot)
        else:
            await self.player_inventory_repository.update(character_slot)

        stored = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='stored'
        )
        if stored:
            stored.quantity += 1
            await self.player_inventory_repository.update(stored)
        else:
            await self.player_inventory_repository.insert(PlayerInventory(
                player_id=player_profile.player.player_id,
                catalogue_id=catalogue_item.catalogue_id,
                status='stored',
                quantity=1
            ))
