from collections.abc import Iterator

from ant_colony.components.resources import ResourcePortion


class Inventory:
    def __init__(
        self,
        capacity: int = 1,
    ) -> None:
        if capacity < 0:
            raise ValueError(
                "Inventory capacity cannot be negative."
            )

        self._capacity = capacity
        self._items: list[ResourcePortion] = []

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def items(self) -> tuple[ResourcePortion, ...]:
        return tuple(self._items)

    @property
    def is_empty(self) -> bool:
        return not self._items

    @property
    def is_full(self) -> bool:
        return len(self._items) >= self._capacity

    @property
    def total_value(self) -> int:
        return sum(
            item.value
            for item in self._items
        )

    def add(
        self,
        item: ResourcePortion,
    ) -> bool:
        if self.is_full:
            return False

        self._items.append(item)
        return True

    def remove(
        self,
        item: ResourcePortion,
    ) -> bool:
        try:
            self._items.remove(item)
        except ValueError:
            return False

        return True

    def clear(self) -> tuple[ResourcePortion, ...]:
        removed_items = self.items
        self._items.clear()
        return removed_items

    def count(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[ResourcePortion]:
        return iter(self._items)

    def __len__(self) -> int:
        return self.count()