from attr import dataclass

from infrastructure import TransportRepository, BusinessInventoryRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Transport, BusinessInventory, RecordNotFoundException, UpdateFailedException

@dataclass
class CompleteTransportCommandRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class CompleteTransportCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    completed: list[Transport]

class CompleteTransportCommand:

    def __init__(self, request: CompleteTransportCommandRequest):
        self.request = request

    async def execute(self) -> CompleteTransportCommandResponse:
        self.transport_repository = await TransportRepository().get_instance()
        self.business_inventory_repository = await BusinessInventoryRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        arrived = await self.transport_repository.get_arrived(player_profile.player.player_id)
        if not arrived:
            raise RecordNotFoundException("No transports have arrived yet.")

        # Bulk-load destination inventory for all arrived transports upfront
        dest_business_ids = {t.to_business_id for t in arrived}
        all_dest_inventory = []
        for bid in dest_business_ids:
            all_dest_inventory.extend(await self.business_inventory_repository.get_all_by_business(bid))
        dest_inv_map = {(i.business_id, i.catalogue_id): i for i in all_dest_inventory}

        completed = []
        for transport in arrived:
            inventory = dest_inv_map.get((transport.to_business_id, transport.catalogue_id))
            if inventory:
                inventory.quantity += transport.quantity
                updated = await self.business_inventory_repository.update(inventory)
            else:
                new_inventory = BusinessInventory(
                    business_id=transport.to_business_id,
                    catalogue_id=transport.catalogue_id,
                    quantity=transport.quantity,
                )
                updated = await self.business_inventory_repository.insert(new_inventory)

            if not updated:
                raise UpdateFailedException(f"Failed to deliver inventory for transport {transport.transport_id}.")

            transport.status = 'arrived'
            transport_updated = await self.transport_repository.update(transport)
            if not transport_updated:
                raise UpdateFailedException(f"Failed to mark transport {transport.transport_id} as arrived.")

            completed.append(transport)

        return CompleteTransportCommandResponse(success=True, server_config=server_config, player=player_profile, completed=completed)
