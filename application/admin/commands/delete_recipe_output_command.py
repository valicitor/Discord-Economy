from attr import dataclass
from infrastructure import RecipeOutputRepository
from domain import RecordNotFoundException, DeleteFailedException


@dataclass
class DeleteRecipeOutputCommandRequest:
    recipe_id: int
    catalogue_id: int


@dataclass
class DeleteRecipeOutputCommandResponse:
    success: bool
    recipe_id: int
    catalogue_id: int


class DeleteRecipeOutputCommand:

    def __init__(self, request: DeleteRecipeOutputCommandRequest):
        self.request = request

    async def execute(self) -> DeleteRecipeOutputCommandResponse:
        repo = await RecipeOutputRepository().get_instance()

        outputs = await repo.get_all_by_recipe(self.request.recipe_id)
        match = next((o for o in outputs if o.catalogue_id == self.request.catalogue_id), None)
        if not match:
            raise RecordNotFoundException(f"Output catalogue_id {self.request.catalogue_id} not found on recipe {self.request.recipe_id}.")

        deleted = await repo.delete(match)
        if not deleted:
            raise DeleteFailedException("Failed to remove recipe output.")

        return DeleteRecipeOutputCommandResponse(
            success=True,
            recipe_id=self.request.recipe_id,
            catalogue_id=self.request.catalogue_id,
        )
