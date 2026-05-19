from domain import Recipe, RecipeInput, RecipeOutput, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, RecipeRepository, RecipeInputRepository, RecipeOutputRepository, CatalogueRepository


class RecipesSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.recipe_repo: RecipeRepository | None = None
        self.input_repo: RecipeInputRepository | None = None
        self.output_repo: RecipeOutputRepository | None = None
        self.catalogue_repo: CatalogueRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.recipe_repo = await RecipeRepository().get_instance()
        seeder.input_repo = await RecipeInputRepository().get_instance()
        seeder.output_repo = await RecipeOutputRepository().get_instance()
        seeder.catalogue_repo = await CatalogueRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "recipes_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "recipes" not in data or "data" not in data["recipes"]:
            raise SeederErrorException("Invalid recipes seed structure")

        inserted = 0
        skipped = 0
        failed = 0

        async with self.recipe_repo.transaction():
            existing = await self.recipe_repo.get_all_by_server(self.server_id)
            if existing:
                return SeederResult(
                    status="skipped",
                    reason="already seeded",
                    inserted=0,
                    failed=0,
                )

            for r in data["recipes"]["data"]:
                try:
                    recipe = Recipe(
                        server_id=self.server_id,
                        name=r["name"],
                    )
                    recipe_id = await self.recipe_repo.insert(recipe)
                    if not recipe_id:
                        failed += 1
                        continue

                    for inp in r.get("inputs", []):
                        catalogue_entry = await self.catalogue_repo.get_by_name(inp["catalogue_name"], self.server_id)
                        if not catalogue_entry:
                            failed += 1
                            continue
                        recipe_input = RecipeInput(
                            recipe_id=recipe_id,
                            catalogue_id=catalogue_entry.catalogue_id,
                            quantity=inp.get("quantity", 1),
                        )
                        await self.input_repo.insert(recipe_input)

                    for out in r.get("outputs", []):
                        catalogue_entry = await self.catalogue_repo.get_by_name(out["catalogue_name"], self.server_id)
                        if not catalogue_entry:
                            failed += 1
                            continue
                        recipe_output = RecipeOutput(
                            recipe_id=recipe_id,
                            catalogue_id=catalogue_entry.catalogue_id,
                            quantity=out.get("quantity", 1),
                        )
                        await self.output_repo.insert(recipe_output)

                    inserted += 1
                except Exception:
                    failed += 1

        return SeederResult(
            status="completed",
            inserted=inserted,
            failed=failed,
        )
