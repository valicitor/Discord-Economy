from attr import dataclass
from infrastructure import ResourceNodeRepository, LocationRepository
from application import DiscordGuild
from application.services.helpers import Helpers
from domain import ResourceNode, CreateFailedException, RecordNotFoundException


@dataclass
class CreateResourceNodeCommandRequest:
    guild: DiscordGuild
    location_id: int
    resource_type: str
    max_quantity: int
    regen_rate: int
    discovered: bool = False


@dataclass
class CreateResourceNodeCommandResponse:
    success: bool
    node: ResourceNode


class CreateResourceNodeCommand:

    def __init__(self, request: CreateResourceNodeCommandRequest):
        self.request = request

    async def execute(self) -> CreateResourceNodeCommandResponse:
        location_repo = await LocationRepository().get_instance()
        node_repo = await ResourceNodeRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        location = await location_repo.get_by_id(self.request.location_id)
        if not location:
            raise RecordNotFoundException(f"Location {self.request.location_id} not found.")

        node = ResourceNode(
            server_id=server_config.server.server_id,
            location_id=self.request.location_id,
            resource_type=self.request.resource_type,
            quantity=self.request.max_quantity,
            max_quantity=self.request.max_quantity,
            regen_rate=self.request.regen_rate,
            discovered=self.request.discovered,
        )
        node_id = await node_repo.insert(node)
        if not node_id:
            raise CreateFailedException("Failed to create resource node.")

        node.node_id = node_id
        return CreateResourceNodeCommandResponse(success=True, node=node)
