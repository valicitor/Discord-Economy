from attr import dataclass
from infrastructure import RecipeInputRepository, RecipeRepository, CatalogueRepository
from domain import RecipeInput, CreateFailedException, RecordNotFoundException, DuplicateRecordException


@dataclass
class CreateRecipeInputCommandRequest:
    recipe_id: int
    catalogue_id: int
    quantity: int


@dataclass
class CreateRecipeInputCommandResponse:
    success: bool
    recipe_input: RecipeInput


class CreateRecipeInputCommand:

    def __init__(self, request: CreateRecipeInputCommandRequest):
        self.request = request

    async def execute(self) -> CreateRecipeInputCommandResponse:
        recipe_repo = await RecipeRepository().get_instance()
        catalogue_repo = await CatalogueRepository().get_instance()
        input_repo = await RecipeInputRepository().get_instance()

        recipe = await recipe_repo.get_by_id(self.request.recipe_id)
        if not recipe:
            raise RecordNotFoundException(f"Recipe {self.request.recipe_id} not found.")

        catalogue_entry = await catalogue_repo.get_by_id(self.request.catalogue_id)
        if not catalogue_entry:
            raise RecordNotFoundException(f"Catalogue entry {self.request.catalogue_id} not found.")

        existing = await input_repo.get_all_by_recipe(self.request.recipe_id)
        if any(i.catalogue_id == self.request.catalogue_id for i in existing):
            raise DuplicateRecordException(f"Input catalogue_id {self.request.catalogue_id} already exists on recipe {self.request.recipe_id}.")

        recipe_input = RecipeInput(
            recipe_id=self.request.recipe_id,
            catalogue_id=self.request.catalogue_id,
            quantity=self.request.quantity,
        )
        input_id = await input_repo.insert(recipe_input)
        if not input_id:
            raise CreateFailedException("Failed to add recipe input.")

        recipe_input.input_id = input_id
        return CreateRecipeInputCommandResponse(success=True, recipe_input=recipe_input)
