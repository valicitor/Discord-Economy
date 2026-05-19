from attr import dataclass
from infrastructure import RecipeRepository
from domain import Recipe, RecordNotFoundException, UpdateFailedException


@dataclass
class UpdateRecipeCommandRequest:
    recipe_id: int
    name: str | None = None


@dataclass
class UpdateRecipeCommandResponse:
    success: bool
    recipe: Recipe


class UpdateRecipeCommand:

    def __init__(self, request: UpdateRecipeCommandRequest):
        self.request = request

    async def execute(self) -> UpdateRecipeCommandResponse:
        repo = await RecipeRepository().get_instance()

        recipe = await repo.get_by_id(self.request.recipe_id)
        if not recipe:
            raise RecordNotFoundException(f"Recipe {self.request.recipe_id} not found.")

        if self.request.name is not None:
            recipe.name = self.request.name

        updated = await repo.update(recipe)
        if not updated:
            raise UpdateFailedException("Failed to update recipe.")

        return UpdateRecipeCommandResponse(success=True, recipe=recipe)
