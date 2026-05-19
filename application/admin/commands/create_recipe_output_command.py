from attr import dataclass
from infrastructure import RecipeOutputRepository, RecipeRepository, CatalogueRepository
from domain import RecipeOutput, CreateFailedException, RecordNotFoundException, DuplicateRecordException


@dataclass
class CreateRecipeOutputCommandRequest:
    recipe_id: int
    catalogue_id: int
    quantity: int


@dataclass
class CreateRecipeOutputCommandResponse:
    success: bool
    recipe_output: RecipeOutput


class CreateRecipeOutputCommand:

    def __init__(self, request: CreateRecipeOutputCommandRequest):
        self.request = request

    async def execute(self) -> CreateRecipeOutputCommandResponse:
        recipe_repo = await RecipeRepository().get_instance()
        catalogue_repo = await CatalogueRepository().get_instance()
        output_repo = await RecipeOutputRepository().get_instance()

        recipe = await recipe_repo.get_by_id(self.request.recipe_id)
        if not recipe:
            raise RecordNotFoundException(f"Recipe {self.request.recipe_id} not found.")

        catalogue_entry = await catalogue_repo.get_by_id(self.request.catalogue_id)
        if not catalogue_entry:
            raise RecordNotFoundException(f"Catalogue entry {self.request.catalogue_id} not found.")

        existing = await output_repo.get_all_by_recipe(self.request.recipe_id)
        if any(o.catalogue_id == self.request.catalogue_id for o in existing):
            raise DuplicateRecordException(f"Output catalogue_id {self.request.catalogue_id} already exists on recipe {self.request.recipe_id}.")

        recipe_output = RecipeOutput(
            recipe_id=self.request.recipe_id,
            catalogue_id=self.request.catalogue_id,
            quantity=self.request.quantity,
        )
        output_id = await output_repo.insert(recipe_output)
        if not output_id:
            raise CreateFailedException("Failed to add recipe output.")

        recipe_output.output_id = output_id
        return CreateRecipeOutputCommandResponse(success=True, recipe_output=recipe_output)
