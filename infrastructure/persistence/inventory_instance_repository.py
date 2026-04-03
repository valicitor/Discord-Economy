from domain import InventoryInstance
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class InventoryInstanceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS inventory_instances (
                    instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, instance_id: int) -> Optional[InventoryInstance]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM inventory_instances WHERE instance_id = ?", (instance_id,)
            )
            row = c.fetchone()
            return InventoryInstance(data=dict(row)) if row else None

    def get_all(self) -> List[InventoryInstance]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM inventory_instances")
            return [InventoryInstance(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, inventory_instance: InventoryInstance) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO inventory_instances (
                    player_id, item_id, metadata
                )
                VALUES (?, ?, ?)
            """, (
                inventory_instance.player_id,
                inventory_instance.item_id,
                str(inventory_instance.metadata)
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, inventory_instance: InventoryInstance) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE inventory_instances
                SET player_id = ?, item_id = ?, metadata = ?
                WHERE instance_id = ?
            """, (
                inventory_instance.player_id,
                inventory_instance.item_id,
                str(inventory_instance.metadata),
                inventory_instance.instance_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, inventory_instance: InventoryInstance) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM inventory_instances WHERE instance_id = ?",
                (inventory_instance.instance_id,)
            )

            self.commit()
            return c.rowcount > 0

    def exists(self, instance_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM inventory_instances WHERE instance_id = ?", (instance_id,)
            )
            return c.fetchone() is not None