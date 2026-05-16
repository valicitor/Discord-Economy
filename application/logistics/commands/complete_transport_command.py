from attr import dataclass

from infrastructure import TransportRepository, BusinessResourceRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Transport, BusinessResource, RecordNotFoundException, UpdateFailedException

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
        self.business_resource_repository = await BusinessResourceRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        arrived = await self.transport_repository.get_arrived(player_profile.player.player_id)
        if not arrived:
            raise RecordNotFoundException("No transports have arrived yet.")

        completed = []
        for transport in arrived:
            resource = await self.business_resource_repository.get_by_business_type(transport.to_business_id, transport.resource_type)
            if resource:
                resource.quantity += transport.quantity
                updated = await self.business_resource_repository.update(resource)
            else:
                new_resource = BusinessResource(
                    business_id=transport.to_business_id,
                    resource_type=transport.resource_type,
                    quantity=transport.quantity,
                    required_quantity=0
                )
                updated = await self.business_resource_repository.insert(new_resource)

            if not updated:
                raise UpdateFailedException(f"Failed to deliver resources for transport {transport.transport_id}.")

            transport.status = 'arrived'
            transport_updated = await self.transport_repository.update(transport)
            if not transport_updated:
                raise UpdateFailedException(f"Failed to mark transport {transport.transport_id} as arrived.")

            completed.append(transport)

        return CompleteTransportCommandResponse(success=True, server_config=server_config, player=player_profile, completed=completed)
