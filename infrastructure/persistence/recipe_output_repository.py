from domain import RecipeOutput, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RecipeOutputRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipe_outputs (
                output_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        await super().execute("DROP TABLE IF EXISTS recipe_outputs")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM recipe_outputs")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "recipe_outputs")
        return affected > 0

    async def get_by_id(self, output_id: int) -> Optional[RecipeOutput]:
        row = await super().fetchrow("SELECT * FROM recipe_outputs WHERE output_id = ?", output_id)
        return RecipeOutput(data=dict(row)) if row else None

    async def get_all(self) -> List[RecipeOutput]:
        rows = await super().fetch("SELECT * FROM recipe_outputs")
        return [RecipeOutput(data=dict(row)) for row in rows]

    async def get_all_by_recipe(self, recipe_id: int) -> List[RecipeOutput]:
        rows = await super().fetch("SELECT * FROM recipe_outputs WHERE recipe_id = ?", recipe_id)
        return [RecipeOutput(data=dict(row)) for row in rows]

    async def exists(self, output_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM recipe_outputs WHERE output_id = ?", output_id)
        return row is not None

    async def insert(self, recipe_output: RecipeOutput) -> int:
        return await super().insert(
            "INSERT INTO recipe_outputs (recipe_id, catalogue_id, quantity) VALUES (?, ?, ?)",
            recipe_output.recipe_id, recipe_output.catalogue_id, recipe_output.quantity
        )

    async def update(self, recipe_output: RecipeOutput) -> bool:
        affected = await super().update(
            "UPDATE recipe_outputs SET recipe_id = ?, catalogue_id = ?, quantity = ? WHERE output_id = ?",
            recipe_output.recipe_id, recipe_output.catalogue_id, recipe_output.quantity, recipe_output.output_id
        )
        return affected > 0

    async def delete(self, recipe_output: RecipeOutput) -> bool:
        affected = await super().delete("DELETE FROM recipe_outputs WHERE output_id = ?", recipe_output.output_id)
        return affected > 0

    async def delete_all(self, recipe_id: int = None) -> bool:
        if recipe_id:
            affected = await super().delete("DELETE FROM recipe_outputs WHERE recipe_id = ?", recipe_id)
        else:
            affected = await super().delete("DELETE FROM recipe_outputs")
        return affected > 0
