from typing import Generic, TypeVar, Union, Iterator

T = TypeVar("T")

class BaseCollection(Generic[T]):
    def __init__(self, items: list[T]):
        if not isinstance(items, list):
            raise TypeError("items must be a list")
        self._items = items

    def __getitem__(self, index: Union[int, slice]) -> Union[T, list[T]]:
        return self._items[index]

    def __setitem__(self, index: Union[int, slice], value: Union[T, list[T]]):
        self._items[index] = value

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __repr__(self):
        return repr(self._items)
    
    def append(self, item: T):
        self._items.append(item)

    def extend(self, items: list[T]):
        self._items.extend(items)

    def remove(self, item: T):
        self._items.remove(item)

    def pop(self, index: int = -1) -> T:
        return self._items.pop(index)