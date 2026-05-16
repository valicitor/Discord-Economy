from domain import Recipe, RecipeIngredient, BusinessResource, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, RecipeRepository, RecipeIngredientRepository, BusinessRepository, BusinessResourceRepository


class RecipesSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.recipe_repo: RecipeRepository | None = None
        self.ingredient_repo: RecipeIngredientRepository | None = None
        self.business_repo: BusinessRepository | None = None
        self.business_resource_repo: BusinessResourceRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.recipe_repo = await RecipeRepository().get_instance()
        seeder.ingredient_repo = await RecipeIngredientRepository().get_instance()
        seeder.business_repo = await BusinessRepository().get_instance()
        seeder.business_resource_repo = await BusinessResourceRepository().get_instance()

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
            existing = await self.recipe_repo.get_all()
            if existing:
                return SeederResult(
                    status="skipped",
                    reason="already seeded",
                    inserted=0,
                    failed=0,
                )

            for r in data["recipes"]["data"]:
                try:
                    business = await self.business_repo.get_by_name(r["business_name"], self.server_id)
                    if not business:
                        skipped += 1
                        continue

                    recipe = Recipe(
                        business_id=business.business_id,
                        name=r["name"],
                        output_type=r["output_type"],
                        output_resource_type=r.get("output_resource_type"),
                        output_catalogue_id=r.get("output_catalogue_id"),
                        output_quantity=r.get("output_quantity", 1),
                    )
                    recipe_id = await self.recipe_repo.insert(recipe)
                    if not recipe_id:
                        failed += 1
                        continue

                    for ing in r.get("ingredients", []):
                        ingredient = RecipeIngredient(
                            recipe_id=recipe_id,
                            resource_type=ing["resource_type"],
                            quantity=ing.get("quantity", 1),
                        )
                        await self.ingredient_repo.insert(ingredient)

                    inserted += 1
                except Exception:
                    failed += 1

            for br_data in data.get("business_resources", {}).get("data", []):
                try:
                    business = await self.business_repo.get_by_name(br_data["business_name"], self.server_id)
                    if not business:
                        skipped += 1
                        continue

                    existing_br = await self.business_resource_repo.get_by_business_type(
                        business.business_id, br_data["resource_type"]
                    )
                    if existing_br:
                        continue

                    br = BusinessResource(
                        business_id=business.business_id,
                        resource_type=br_data["resource_type"],
                        quantity=br_data.get("quantity", 0),
                        required_quantity=br_data.get("required_quantity", 0),
                    )
                    await self.business_resource_repo.insert(br)
                except Exception:
                    failed += 1

        return SeederResult(
            status="completed",
            inserted=inserted,
            failed=failed,
        )
