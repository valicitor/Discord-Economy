from attr import dataclass
from infrastructure import RecipeRepository, RecipeInputRepository, RecipeOutputRepository
from domain import RecordNotFoundException, DeleteFailedException


@dataclass
class DeleteRecipeCommandRequest:
    recipe_id: int


@dataclass
class DeleteRecipeCommandResponse:
    success: bool
    recipe_id: int


class DeleteRecipeCommand:

    def __init__(self, request: DeleteRecipeCommandRequest):
        self.request = request

    async def execute(self) -> DeleteRecipeCommandResponse:
        recipe_repo = await RecipeRepository().get_instance()
        input_repo = await RecipeInputRepository().get_instance()
        output_repo = await RecipeOutputRepository().get_instance()

        recipe = await recipe_repo.get_by_id(self.request.recipe_id)
        if not recipe:
            raise RecordNotFoundException(f"Recipe {self.request.recipe_id} not found.")

        await input_repo.delete_all(self.request.recipe_id)
        await output_repo.delete_all(self.request.recipe_id)

        deleted = await recipe_repo.delete(recipe)
        if not deleted:
            raise DeleteFailedException("Failed to delete recipe.")

        return DeleteRecipeCommandResponse(success=True, recipe_id=self.request.recipe_id)
