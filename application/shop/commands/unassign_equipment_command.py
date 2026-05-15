import json

from attr import dataclass

from infrastructure import PlayerInventoryRepository, CatalogueRepository, PlayerUnitRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import PlayerInventory, PlayerUnit, InvalidDataException, RecordNotFoundException, UpdateFailedException

@dataclass
class UnassignEquipmentCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    unit_name: str
    slot_name: str

@dataclass
class UnassignEquipmentCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    unit: PlayerUnit
    unassigned_item: str

class UnassignEquipmentCommand:

    def __init__(self, request: UnassignEquipmentCommandRequest):
        self.request = request

    async def execute(self) -> UnassignEquipmentCommandResponse:
        self.player_inventory_repository = await PlayerInventoryRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()
        self.player_unit_repository = await PlayerUnitRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        unassigned_item = None
        async with self.player_inventory_repository.transaction():
            unit = await self.player_unit_repository.get_by_name(self.request.unit_name, player_profile.player.player_id)
            if not unit:
                raise RecordNotFoundException(f"Unit '{self.request.unit_name}' not found.")

            metadata = unit.metadata if isinstance(unit.metadata, dict) else json.loads(unit.metadata)
            assigned = metadata.get("assigned", {})
            if not isinstance(assigned, dict):
                raise InvalidDataException("Unit assignment data is invalid.")

            if self.request.slot_name not in assigned:
                raise InvalidDataException(f"Slot '{self.request.slot_name}' has no equipment assigned.")

            unassigned_item = assigned.pop(self.request.slot_name)
            unit.metadata = {**metadata, "assigned": assigned}

            gear_catalogue = await self.catalogue_repository.get_by_name(unassigned_item, server_config.server.server_id)
            if gear_catalogue:
                await self._return_to_stored(player_profile, gear_catalogue)

            if not await self.player_unit_repository.update(unit):
                raise UpdateFailedException("Failed to update unit.")

        return UnassignEquipmentCommandResponse(
            success=True,
            server_config=server_config,
            player=player_profile,
            unit=unit,
            unassigned_item=unassigned_item
        )

    async def _return_to_stored(self, player_profile: PlayerProfile, gear_catalogue) -> None:
        equipped = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, gear_catalogue.catalogue_id, status='equipped'
        )
        if equipped:
            equipped.quantity -= 1
            if equipped.quantity == 0:
                await self.player_inventory_repository.delete(equipped)
            else:
                await self.player_inventory_repository.update(equipped)

        stored = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, gear_catalogue.catalogue_id, status='stored'
        )
        if stored:
            stored.quantity += 1
            await self.player_inventory_repository.update(stored)
        else:
            await self.player_inventory_repository.insert(PlayerInventory(
                player_id=player_profile.player.player_id,
                catalogue_id=gear_catalogue.catalogue_id,
                status='stored',
                quantity=1
            ))
