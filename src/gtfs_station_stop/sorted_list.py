from typing import TYPE_CHECKING, Any, Iterable, Iterator, Self, SupportsIndex, overload
from bisect import insort, bisect_left, bisect_right

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison


class SortedList[T: SupportsRichComparison]:
    _items: list[T]

    @overload
    def __init__(self) -> None: ...
    """Creates an empty SortedList"""

    @overload
    def __init__(self, iterable: Iterable[T]) -> None: ...
    """Creates a SortedList based on the contents of an iterable"""

    def __init__(self, iterable: Iterable | None = None) -> None:
        self._items = sorted(iterable) if iterable is not None else []

    @classmethod
    def _from_already_sorted(cls, items: list[T]) -> Self:
        instance = cls.__new__(cls)

        instance._items = items

        return instance

    def add(self, element: T) -> None:
        # use binary search to find place for element

        insort(self._items, element)

    def __len__(self) -> int:
        return len(self._items)

    def __add__(self, other: Iterable[T]) -> SortedList[T]:
        output = SortedList(self)

        output.extend(other)

        return output

    def __iter__(self) -> Iterator[T]:
        return self._items.__iter__()

    def __contains__(self, key: T) -> bool:
        pos = bisect_left(self._items, key)

        if pos == len(self):
            return False

        return self[pos] == key

    def __delitem__(self, key: SupportsIndex | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None]) -> None:
        self._items.__delitem__(key)

    @overload
    def __getitem__(self, key: SupportsIndex) -> T: ...

    @overload
    def __getitem__(self, key: slice[SupportsIndex | None, SupportsIndex |
                    None, SupportsIndex | None]) -> list[T]: ...

    def __getitem__(self, key: SupportsIndex | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None]) -> SupportsRichComparison | list[SupportsRichComparison]:
        return self._items.__getitem__(key)

    def __getstate__(self) -> object:
        return self._items.__getstate__()

    def __iadd__(self, other: Iterable[T]) -> Self:
        for item in other:
            self.add(item)

        return self

    def __imul__(self, other: SupportsIndex) -> Self:
        self._items = [item for item in self._items for i in range(other)]

        return self

    def __mul__(self, other: SupportsIndex) -> SortedList:
        return self._from_already_sorted([item for item in self._items for i in range(other)])

    def __reduce__(self) -> str | tuple[Any, ...]:
        return self._items.__reduce__()

    def __repr__(self) -> str:
        return f"SortedList{self._items.__repr__()}"

    def __rmul__(self, other) -> SortedList:
        return self.__mul__(other)

    def __reversed__(self) -> Iterator[T]:
        return self._items.__reversed__()

    def index(self, item: T, start: SupportsIndex = 0, stop: SupportsIndex | None = None) -> int:
        idx = bisect_left(self._items, item, start.__index__(),
                          stop.__index__() if stop is not None else None)

        if idx == len(self) or self[idx] != item:
            raise ValueError("Item not present")

        return idx

    def extend(self, iterable: Iterable[T]) -> None:
        self += iterable

    def clear(self) -> None:
        self._items.clear()

    def search_range(self, start_item: T | None = None, end_item: T | None = None) -> slice[int, int, None]:
        start_index = bisect_left(
            self._items, start_item) if start_item is not None else 0
        end_index = bisect_right(
            self._items, end_item) if end_item is not None else (len(self) - 1)
        return slice(start_index, end_index)
