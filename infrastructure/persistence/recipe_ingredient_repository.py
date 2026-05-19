from domain import RecipeInput, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RecipeInputRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipe_inputs (
                input_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                catalogue_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                FOREIGN KEY(catalogue_id) REFERENCES catalogue(catalogue_id),
                UNIQUE(recipe_id, catalogue_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS recipe_inputs")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM recipe_inputs")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "recipe_inputs")
        return affected > 0

    async def get_by_id(self, input_id: int) -> Optional[RecipeInput]:
        row = await super().fetchrow("SELECT * FROM recipe_inputs WHERE input_id = ?", input_id)
        return RecipeInput(data=dict(row)) if row else None

    async def get_all(self) -> List[RecipeInput]:
        rows = await super().fetch("SELECT * FROM recipe_inputs")
        return [RecipeInput(data=dict(row)) for row in rows]

    async def get_all_by_recipe(self, recipe_id: int) -> List[RecipeInput]:
        rows = await super().fetch("SELECT * FROM recipe_inputs WHERE recipe_id = ?", recipe_id)
        return [RecipeInput(data=dict(row)) for row in rows]

    async def exists(self, input_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM recipe_inputs WHERE input_id = ?", input_id)
        return row is not None

    async def insert(self, recipe_input: RecipeInput) -> int:
        return await super().insert(
            "INSERT INTO recipe_inputs (recipe_id, catalogue_id, quantity) VALUES (?, ?, ?)",
            recipe_input.recipe_id, recipe_input.catalogue_id, recipe_input.quantity
        )

    async def update(self, recipe_input: RecipeInput) -> bool:
        affected = await super().update(
            "UPDATE recipe_inputs SET recipe_id = ?, catalogue_id = ?, quantity = ? WHERE input_id = ?",
            recipe_input.recipe_id, recipe_input.catalogue_id, recipe_input.quantity, recipe_input.input_id
        )
        return affected > 0

    async def delete(self, recipe_input: RecipeInput) -> bool:
        affected = await super().delete("DELETE FROM recipe_inputs WHERE input_id = ?", recipe_input.input_id)
        return affected > 0

    async def delete_all(self, recipe_id: int = None) -> bool:
        if recipe_id:
            affected = await super().delete("DELETE FROM recipe_inputs WHERE recipe_id = ?", recipe_id)
        else:
            affected = await super().delete("DELETE FROM recipe_inputs")
        return affected > 0
