from attr import dataclass
from infrastructure import ResourceNodeRepository
from domain import RecordNotFoundException, DeleteFailedException


@dataclass
class DeleteResourceNodeCommandRequest:
    node_id: int


@dataclass
class DeleteResourceNodeCommandResponse:
    success: bool
    node_id: int


class DeleteResourceNodeCommand:

    def __init__(self, request: DeleteResourceNodeCommandRequest):
        self.request = request

    async def execute(self) -> DeleteResourceNodeCommandResponse:
        repo = await ResourceNodeRepository().get_instance()

        node = await repo.get_by_id(self.request.node_id)
        if not node:
            raise RecordNotFoundException(f"Resource node {self.request.node_id} not found.")

        deleted = await repo.delete(node)
        if not deleted:
            raise DeleteFailedException("Failed to delete resource node.")

        return DeleteResourceNodeCommandResponse(success=True, node_id=self.request.node_id)
