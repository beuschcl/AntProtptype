from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoodPortion:
    source_id: int | str
    nutrition: int

    def __post_init__(self) -> None:
        if self.nutrition <= 0:
            raise ValueError(
                "Food nutrition must be greater than zero."
            )


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
        self._items: list[FoodPortion] = []

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def items(self) -> tuple[FoodPortion, ...]:
        return tuple(self._items)

    @property
    def is_empty(self) -> bool:
        return not self._items

    @property
    def is_full(self) -> bool:
        return len(self._items) >= self._capacity

    @property
    def total_nutrition(self) -> int:
        return sum(
            item.nutrition
            for item in self._items
        )

    def add(
        self,
        item: FoodPortion,
    ) -> bool:
        if self.is_full:
            return False

        self._items.append(item)
        return True

    def remove(
        self,
        item: FoodPortion,
    ) -> bool:
        try:
            self._items.remove(item)
        except ValueError:
            return False

        return True

    def clear(self) -> tuple[FoodPortion, ...]:
        removed_items = self.items
        self._items.clear()
        return removed_items

    def count(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[FoodPortion]:
        return iter(self._items)

    def __len__(self) -> int:
        return self.count()