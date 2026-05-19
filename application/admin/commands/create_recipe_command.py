from attr import dataclass
from infrastructure import RecipeRepository
from application import DiscordGuild
from application.services.helpers import Helpers
from domain import Recipe, CreateFailedException


@dataclass
class CreateRecipeCommandRequest:
    guild: DiscordGuild
    name: str


@dataclass
class CreateRecipeCommandResponse:
    success: bool
    recipe: Recipe


class CreateRecipeCommand:

    def __init__(self, request: CreateRecipeCommandRequest):
        self.request = request

    async def execute(self) -> CreateRecipeCommandResponse:
        recipe_repo = await RecipeRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        recipe = Recipe(
            server_id=server_config.server.server_id,
            name=self.request.name,
        )
        recipe_id = await recipe_repo.insert(recipe)
        if not recipe_id:
            raise CreateFailedException("Failed to create recipe.")

        recipe.recipe_id = recipe_id
        return CreateRecipeCommandResponse(success=True, recipe=recipe)
