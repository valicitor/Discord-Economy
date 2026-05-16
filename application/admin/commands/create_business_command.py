from attr import dataclass

from infrastructure import BusinessRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Business, CreateFailedException, DuplicateRecordException

@dataclass
class CreateBusinessCommandRequest:
    guild: DiscordGuild
    name: str
    description: str
    type: str
    x: int
    y: int
    range: int | None = None

@dataclass
class CreateBusinessCommandResponse:
    success: bool
    server_config: ServerConfig
    business: Business

class CreateBusinessCommand:

    def __init__(self, request: CreateBusinessCommandRequest):
        self.request = request

    async def execute(self) -> CreateBusinessCommandResponse:
        self.business_repository = await BusinessRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        existing = await self.business_repository.get_by_name(self.request.name, server_config.server.server_id)
        if existing:
            raise DuplicateRecordException(f"A business named '{self.request.name}' already exists.")

        new_business = Business(
            server_id=server_config.server.server_id,
            name=self.request.name,
            description=self.request.description,
            type=self.request.type,
            x=self.request.x,
            y=self.request.y,
            range=self.request.range,
        )
        business_id = await self.business_repository.insert(new_business)
        if not business_id:
            raise CreateFailedException("Failed to create business.")

        new_business.business_id = business_id
        return CreateBusinessCommandResponse(success=True, server_config=server_config, business=new_business)
