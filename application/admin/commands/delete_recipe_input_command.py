from attr import dataclass
from infrastructure import RecipeInputRepository
from domain import RecordNotFoundException, DeleteFailedException


@dataclass
class DeleteRecipeInputCommandRequest:
    recipe_id: int
    catalogue_id: int


@dataclass
class DeleteRecipeInputCommandResponse:
    success: bool
    recipe_id: int
    catalogue_id: int


class DeleteRecipeInputCommand:

    def __init__(self, request: DeleteRecipeInputCommandRequest):
        self.request = request

    async def execute(self) -> DeleteRecipeInputCommandResponse:
        repo = await RecipeInputRepository().get_instance()

        inputs = await repo.get_all_by_recipe(self.request.recipe_id)
        match = next((i for i in inputs if i.catalogue_id == self.request.catalogue_id), None)
        if not match:
            raise RecordNotFoundException(f"Input catalogue_id {self.request.catalogue_id} not found on recipe {self.request.recipe_id}.")

        deleted = await repo.delete(match)
        if not deleted:
            raise DeleteFailedException("Failed to remove recipe input.")

        return DeleteRecipeInputCommandResponse(
            success=True,
            recipe_id=self.request.recipe_id,
            catalogue_id=self.request.catalogue_id,
        )
