from domain import RecipeIngredient, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RecipeIngredientRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                UNIQUE(recipe_id, resource_type)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS recipe_ingredients")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM recipe_ingredients")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "recipe_ingredients")
        return affected > 0

    async def get_by_id(self, ingredient_id: int) -> Optional[RecipeIngredient]:
        row = await super().fetchrow("SELECT * FROM recipe_ingredients WHERE ingredient_id = ?", ingredient_id)
        return RecipeIngredient(data=dict(row)) if row else None

    async def get_all(self) -> List[RecipeIngredient]:
        rows = await super().fetch("SELECT * FROM recipe_ingredients")
        return [RecipeIngredient(data=dict(row)) for row in rows]

    async def get_all_by_recipe(self, recipe_id: int) -> List[RecipeIngredient]:
        rows = await super().fetch("SELECT * FROM recipe_ingredients WHERE recipe_id = ?", recipe_id)
        return [RecipeIngredient(data=dict(row)) for row in rows]

    async def exists(self, ingredient_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM recipe_ingredients WHERE ingredient_id = ?", ingredient_id)
        return row is not None

    async def insert(self, ingredient: RecipeIngredient) -> int:
        return await super().insert(
            "INSERT INTO recipe_ingredients (recipe_id, resource_type, quantity) VALUES (?, ?, ?)",
            ingredient.recipe_id, ingredient.resource_type, ingredient.quantity
        )

    async def update(self, ingredient: RecipeIngredient) -> bool:
        affected = await super().update(
            "UPDATE recipe_ingredients SET recipe_id = ?, resource_type = ?, quantity = ? WHERE ingredient_id = ?",
            ingredient.recipe_id, ingredient.resource_type, ingredient.quantity, ingredient.ingredient_id
        )
        return affected > 0

    async def delete(self, ingredient: RecipeIngredient) -> bool:
        affected = await super().delete("DELETE FROM recipe_ingredients WHERE ingredient_id = ?", ingredient.ingredient_id)
        return affected > 0

    async def delete_all(self, recipe_id: int) -> bool:
        affected = await super().delete("DELETE FROM recipe_ingredients WHERE recipe_id = ?", recipe_id)
        return affected > 0
