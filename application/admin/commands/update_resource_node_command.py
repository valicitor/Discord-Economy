from attr import dataclass
from infrastructure import ResourceNodeRepository
from domain import ResourceNode, RecordNotFoundException, UpdateFailedException


@dataclass
class UpdateResourceNodeCommandRequest:
    node_id: int
    resource_type: str | None = None
    max_quantity: int | None = None
    regen_rate: int | None = None


@dataclass
class UpdateResourceNodeCommandResponse:
    success: bool
    node: ResourceNode


class UpdateResourceNodeCommand:

    def __init__(self, request: UpdateResourceNodeCommandRequest):
        self.request = request

    async def execute(self) -> UpdateResourceNodeCommandResponse:
        repo = await ResourceNodeRepository().get_instance()

        node = await repo.get_by_id(self.request.node_id)
        if not node:
            raise RecordNotFoundException(f"Resource node {self.request.node_id} not found.")

        if self.request.resource_type is not None:
            node.resource_type = self.request.resource_type
        if self.request.max_quantity is not None:
            node.max_quantity = self.request.max_quantity
        if self.request.regen_rate is not None:
            node.regen_rate = self.request.regen_rate

        updated = await repo.update(node)
        if not updated:
            raise UpdateFailedException("Failed to update resource node.")

        return UpdateResourceNodeCommandResponse(success=True, node=node)
