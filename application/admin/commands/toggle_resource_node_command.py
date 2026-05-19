from attr import dataclass
from infrastructure import ResourceNodeRepository
from domain import ResourceNode, RecordNotFoundException, UpdateFailedException


@dataclass
class ToggleResourceNodeCommandRequest:
    node_id: int


@dataclass
class ToggleResourceNodeCommandResponse:
    success: bool
    node: ResourceNode


class ToggleResourceNodeCommand:

    def __init__(self, request: ToggleResourceNodeCommandRequest):
        self.request = request

    async def execute(self) -> ToggleResourceNodeCommandResponse:
        repo = await ResourceNodeRepository().get_instance()

        node = await repo.get_by_id(self.request.node_id)
        if not node:
            raise RecordNotFoundException(f"Resource node {self.request.node_id} not found.")

        node.discovered = not node.discovered
        updated = await repo.update(node)
        if not updated:
            raise UpdateFailedException("Failed to toggle resource node.")

        return ToggleResourceNodeCommandResponse(success=True, node=node)
