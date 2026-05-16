from domain import Recipe, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RecipeRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                output_type TEXT NOT NULL,
                output_resource_type TEXT,
                output_catalogue_id INTEGER,
                output_quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(business_id) REFERENCES businesses(business_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS recipes")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM recipes")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "recipes")
        return affected > 0

    async def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        row = await super().fetchrow("SELECT * FROM recipes WHERE recipe_id = ?", recipe_id)
        return Recipe(data=dict(row)) if row else None

    async def get_all(self) -> List[Recipe]:
        rows = await super().fetch("SELECT * FROM recipes")
        return [Recipe(data=dict(row)) for row in rows]

    async def get_all_by_business(self, business_id: int) -> List[Recipe]:
        rows = await super().fetch("SELECT * FROM recipes WHERE business_id = ?", business_id)
        return [Recipe(data=dict(row)) for row in rows]

    async def exists(self, recipe_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM recipes WHERE recipe_id = ?", recipe_id)
        return row is not None

    async def insert(self, recipe: Recipe) -> int:
        return await super().insert(
            "INSERT INTO recipes (business_id, name, output_type, output_resource_type, output_catalogue_id, output_quantity) VALUES (?, ?, ?, ?, ?, ?)",
            recipe.business_id, recipe.name, recipe.output_type, recipe.output_resource_type, recipe.output_catalogue_id, recipe.output_quantity
        )

    async def update(self, recipe: Recipe) -> bool:
        affected = await super().update(
            "UPDATE recipes SET business_id = ?, name = ?, output_type = ?, output_resource_type = ?, output_catalogue_id = ?, output_quantity = ? WHERE recipe_id = ?",
            recipe.business_id, recipe.name, recipe.output_type, recipe.output_resource_type, recipe.output_catalogue_id, recipe.output_quantity, recipe.recipe_id
        )
        return affected > 0

    async def delete(self, recipe: Recipe) -> bool:
        affected = await super().delete("DELETE FROM recipes WHERE recipe_id = ?", recipe.recipe_id)
        return affected > 0

    async def delete_all(self, business_id: int) -> bool:
        affected = await super().delete("DELETE FROM recipes WHERE business_id = ?", business_id)
        return affected > 0
