from attr import dataclass
from infrastructure import LocationPolicyRepository
from domain import RecordNotFoundException, DeleteFailedException


@dataclass
class DeleteLocationPolicyCommandRequest:
    location_id: int


@dataclass
class DeleteLocationPolicyCommandResponse:
    success: bool
    location_id: int


class DeleteLocationPolicyCommand:

    def __init__(self, request: DeleteLocationPolicyCommandRequest):
        self.request = request

    async def execute(self) -> DeleteLocationPolicyCommandResponse:
        repo = await LocationPolicyRepository().get_instance()

        policy = await repo.get_by_location(self.request.location_id)
        if not policy:
            raise RecordNotFoundException(f"No policy found for location {self.request.location_id}.")

        deleted = await repo.delete(policy)
        if not deleted:
            raise DeleteFailedException("Failed to delete location policy.")

        return DeleteLocationPolicyCommandResponse(success=True, location_id=self.request.location_id)
