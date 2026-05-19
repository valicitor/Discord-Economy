from domain import Recipe, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RecipeRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                UNIQUE(name, server_id)
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

    async def get_all_by_server(self, server_id: int) -> List[Recipe]:
        rows = await super().fetch("SELECT * FROM recipes WHERE server_id = ?", server_id)
        return [Recipe(data=dict(row)) for row in rows]

    async def get_by_name(self, name: str, server_id: int) -> Optional[Recipe]:
        row = await super().fetchrow(
            "SELECT * FROM recipes WHERE name = ? AND server_id = ?", name, server_id
        )
        return Recipe(data=dict(row)) if row else None

    async def exists(self, recipe_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM recipes WHERE recipe_id = ?", recipe_id)
        return row is not None

    async def insert(self, recipe: Recipe) -> int:
        return await super().insert(
            "INSERT INTO recipes (server_id, name) VALUES (?, ?)",
            recipe.server_id, recipe.name
        )

    async def update(self, recipe: Recipe) -> bool:
        affected = await super().update(
            "UPDATE recipes SET server_id = ?, name = ? WHERE recipe_id = ?",
            recipe.server_id, recipe.name, recipe.recipe_id
        )
        return affected > 0

    async def delete(self, recipe: Recipe) -> bool:
        affected = await super().delete("DELETE FROM recipes WHERE recipe_id = ?", recipe.recipe_id)
        return affected > 0

    async def delete_all(self, server_id: int = None) -> bool:
        if server_id:
            affected = await super().delete("DELETE FROM recipes WHERE server_id = ?", server_id)
        else:
            affected = await super().delete("DELETE FROM recipes")
        return affected > 0
