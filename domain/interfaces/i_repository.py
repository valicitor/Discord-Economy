from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> T:
        pass

    @abstractmethod
    async def get_all(self, guild_id: str) -> List[T]:
        pass

    @abstractmethod
    async def add(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def update(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def exists(self, id: str, guild_id: str) -> bool:
        pass