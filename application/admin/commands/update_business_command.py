from attr import dataclass

from infrastructure import BusinessRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Business, UpdateFailedException, RecordNotFoundException

@dataclass
class UpdateBusinessCommandRequest:
    guild: DiscordGuild
    business_id: int
    name: str | None = None
    description: str | None = None
    type: str | None = None
    x: int | None = None
    y: int | None = None
    range: int | None = None

@dataclass
class UpdateBusinessCommandResponse:
    success: bool
    server_config: ServerConfig
    business: Business

class UpdateBusinessCommand:

    def __init__(self, request: UpdateBusinessCommandRequest):
        self.request = request

    async def execute(self) -> UpdateBusinessCommandResponse:
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        business = await self.business_repository.get_by_id(self.request.business_id)
        if not business:
            raise RecordNotFoundException(f"Business with id '{self.request.business_id}' not found.")

        if self.request.name is not None:
            business.name = self.request.name
        if self.request.description is not None:
            business.description = self.request.description
        if self.request.type is not None:
            business.type = self.request.type
        if self.request.x is not None:
            business.x = self.request.x
        if self.request.y is not None:
            business.y = self.request.y
        if self.request.range is not None:
            business.range = self.request.range

        success = await self.business_repository.update(business)
        if not success:
            raise UpdateFailedException("Failed to update business.")

        return UpdateBusinessCommandResponse(success=True, server_config=server_config, business=business)
