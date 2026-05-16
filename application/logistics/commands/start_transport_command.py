import math
from datetime import datetime, timezone, timedelta
from attr import dataclass

from infrastructure import TransportRepository, BusinessRepository, BusinessResourceRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Transport, RecordNotFoundException, InvalidDataException, PermissionDeniedException, UpdateFailedException, CreateFailedException

@dataclass
class StartTransportCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    from_business_id: int
    to_business_id: int
    resource_type: str
    quantity: int

@dataclass
class StartTransportCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    transport: Transport

class StartTransportCommand:

    def __init__(self, request: StartTransportCommandRequest):
        self.request = request

    async def execute(self) -> StartTransportCommandResponse:
        self.transport_repository = await TransportRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()
        self.business_resource_repository = await BusinessResourceRepository().get_instance()

        if self.request.quantity <= 0:
            raise InvalidDataException("Transport quantity must be greater than zero.")

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        from_business = await self.business_repository.get_by_id(self.request.from_business_id)
        if not from_business:
            raise RecordNotFoundException(f"Source business with id '{self.request.from_business_id}' not found.")

        to_business = await self.business_repository.get_by_id(self.request.to_business_id)
        if not to_business:
            raise RecordNotFoundException(f"Destination business with id '{self.request.to_business_id}' not found.")

        if not Helpers.is_in_range(from_business.x, from_business.y, from_business.range, player_profile.player.x, player_profile.player.y):
            raise PermissionDeniedException("You are not close enough to the source business to start a transport.")

        resource = await self.business_resource_repository.get_by_business_type(self.request.from_business_id, self.request.resource_type)
        if not resource or resource.quantity < self.request.quantity:
            raise InvalidDataException(f"Source business does not have {self.request.quantity}x '{self.request.resource_type}'.")

        resource.quantity -= self.request.quantity
        resource_updated = await self.business_resource_repository.update(resource)
        if not resource_updated:
            raise UpdateFailedException("Failed to deduct resources from source business.")

        _, speed_setting = server_config.server_settings.get_by_key("travel_speed")
        travel_speed = int(speed_setting.value) if speed_setting else 10

        dx = to_business.x - from_business.x
        dy = to_business.y - from_business.y
        distance = math.sqrt(dx * dx + dy * dy)
        travel_seconds = int(distance / travel_speed * 60)
        arrive_at = (datetime.now(timezone.utc) + timedelta(seconds=travel_seconds)).strftime("%Y-%m-%d %H:%M:%S")

        transport = Transport(
            player_id=player_profile.player.player_id,
            from_business_id=self.request.from_business_id,
            to_business_id=self.request.to_business_id,
            resource_type=self.request.resource_type,
            quantity=self.request.quantity,
            status='in_transit',
            arrive_at=arrive_at
        )
        transport_id = await self.transport_repository.insert(transport)
        if not transport_id:
            raise CreateFailedException("Failed to start transport. Please try again.")
        transport.transport_id = transport_id

        return StartTransportCommandResponse(success=True, server_config=server_config, player=player_profile, transport=transport)
