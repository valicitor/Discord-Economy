from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):

    #--------- Schema Setup ----------

    @abstractmethod
    async def init_database(self):
        """Initializes the database schema. Called automatically on first use. Override in child classes to create tables."""
        pass

    # ---------- Teardown ----------

    @abstractmethod
    async def drop_table(self):
        """Use with caution! Drops the entire table. Only for testing or if you have a very good reason."""
        pass

    @abstractmethod
    async def clear_all(self) -> bool:
        """Use with caution! Deletes all records in the table. Clear all data for tests, or in production if you have a very good reason."""
        pass

    # ---------- Queries ----------
    @abstractmethod
    async def get_by_id(self, id: str) -> T:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def exists(self, id: str, guild_id: str) -> bool:
        pass

    # ---------- Mutations ----------
    @abstractmethod
    async def insert(self, entity: T) -> int:
        pass

    @abstractmethod
    async def update(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete_all(self) -> bool:
        """Deletes all records in the table, restricts by environment variable such as server_id."""
        pass