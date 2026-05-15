import json

from attr import dataclass

from infrastructure import PlayerInventoryRepository, CatalogueRepository, PlayerUnitRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import PlayerInventory, PlayerUnit, Catalogue, InvalidDataException, RecordNotFoundException, DuplicateRecordException, UpdateFailedException

@dataclass
class CreateCustomUnitCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    unit_name: str
    race_name: str
    equipment: dict[str, str]  # slot_name -> catalogue_item_name

@dataclass
class CreateCustomUnitCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    unit: PlayerUnit

class CreateCustomUnitCommand:

    def __init__(self, request: CreateCustomUnitCommandRequest):
        self.request = request

    async def execute(self) -> CreateCustomUnitCommandResponse:
        self.player_inventory_repository = await PlayerInventoryRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()
        self.player_unit_repository = await PlayerUnitRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        unit = None
        async with self.player_inventory_repository.transaction():
            existing_unit = await self.player_unit_repository.get_by_name(self.request.unit_name, player_profile.player.player_id)
            if existing_unit:
                raise DuplicateRecordException(f"You already have a unit named '{self.request.unit_name}'.")

            race_catalogue = await self.catalogue_repository.get_by_name(self.request.race_name, server_config.server.server_id)
            if not race_catalogue or race_catalogue.type != "Race":
                raise RecordNotFoundException(f"Race '{self.request.race_name}' not found.")

            race_inventory = await self.player_inventory_repository.get_by_player_catalogue_id(
                player_profile.player.player_id, race_catalogue.catalogue_id, status='stored'
            )
            if not race_inventory or race_inventory.quantity < 1:
                raise InvalidDataException(f"You don't have '{self.request.race_name}' in your inventory.")

            race_metadata = json.loads(race_catalogue.metadata) if isinstance(race_catalogue.metadata, str) else race_catalogue.metadata
            if not isinstance(race_metadata, dict):
                raise InvalidDataException("Race metadata is invalid.")
            available_slots = race_metadata.get("slots", {})
            if not isinstance(available_slots, dict):
                raise InvalidDataException("Race slot data is invalid.")

            for slot_name, item_name in self.request.equipment.items():
                if slot_name not in available_slots:
                    raise InvalidDataException(f"Slot '{slot_name}' is not available for race '{self.request.race_name}'.")
                gear_catalogue = await self.catalogue_repository.get_by_name(item_name, server_config.server.server_id)
                if not gear_catalogue:
                    raise RecordNotFoundException(f"Item '{item_name}' not found.")
                gear_inventory = await self.player_inventory_repository.get_by_player_catalogue_id(
                    player_profile.player.player_id, gear_catalogue.catalogue_id, status='stored'
                )
                if not gear_inventory or gear_inventory.quantity < 1:
                    raise InvalidDataException(f"You don't have '{item_name}' in your inventory.")

            await self._move_to_equipped(player_profile, race_catalogue)

            for item_name in self.request.equipment.values():
                gear_catalogue = await self.catalogue_repository.get_by_name(item_name, server_config.server.server_id)
                await self._move_to_equipped(player_profile, gear_catalogue)

            new_unit = PlayerUnit(
                player_id=player_profile.player.player_id,
                name=self.request.unit_name,
                quantity=1,
                custom=1,
                metadata={"slots": available_slots, "assigned": self.request.equipment}
            )
            unit_id = await self.player_unit_repository.insert(new_unit)
            if not unit_id:
                raise UpdateFailedException("Failed to create custom unit.")
            unit = await self.player_unit_repository.get_by_id(unit_id)

        return CreateCustomUnitCommandResponse(
            success=True,
            server_config=server_config,
            player=player_profile,
            unit=unit
        )

    async def _move_to_equipped(self, player_profile: PlayerProfile, catalogue_item: Catalogue) -> None:
        stored = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='stored'
        )
        stored.quantity -= 1
        if stored.quantity == 0:
            await self.player_inventory_repository.delete(stored)
        else:
            await self.player_inventory_repository.update(stored)

        equipped = await self.player_inventory_repository.get_by_player_catalogue_id(
            player_profile.player.player_id, catalogue_item.catalogue_id, status='equipped'
        )
        if equipped:
            equipped.quantity += 1
            await self.player_inventory_repository.update(equipped)
        else:
            await self.player_inventory_repository.insert(PlayerInventory(
                player_id=player_profile.player.player_id,
                catalogue_id=catalogue_item.catalogue_id,
                status='equipped',
                quantity=1
            ))
