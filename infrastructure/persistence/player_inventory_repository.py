from domain import PlayerInventory
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerInventoryRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS player_inventory (
                    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, inventory_id: int) -> Optional[PlayerInventory]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM player_inventory WHERE inventory_id = ?", (inventory_id,)
            )
            row = c.fetchone()
            return PlayerInventory(data=dict(row)) if row else None

    def get_all(self) -> List[PlayerInventory]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM player_inventory")
            return [PlayerInventory(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player_inventory: PlayerInventory) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO player_inventory (
                    player_id, item_id, quantity
                )
                VALUES (?, ?, ?)
            """, (
                player_inventory.player_id,
                player_inventory.item_id,
                player_inventory.quantity
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player_inventory: PlayerInventory) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE player_inventory
                SET quantity = ?
                WHERE inventory_id = ?
            """, (
                player_inventory.quantity,
                player_inventory.inventory_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, player_inventory: PlayerInventory) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM player_inventory WHERE inventory_id = ?",
                (player_inventory.inventory_id,)
            )

            self.commit()
            return c.rowcount > 0

    def exists(self, inventory_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM player_inventory WHERE inventory_id = ?", (inventory_id,)
            )
            return c.fetchone() is not None