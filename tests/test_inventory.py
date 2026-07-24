import pytest

from ant_colony.components import (
    FoodPortion,
    Inventory,
)


def test_inventory_starts_empty() -> None:
    inventory = Inventory(capacity=2)

    assert inventory.items == ()
    assert inventory.is_empty
    assert not inventory.is_full
    assert inventory.count() == 0


def test_inventory_adds_food_portion() -> None:
    inventory = Inventory(capacity=2)
    portion = FoodPortion(
        source_id=1,
        nutrition=5,
    )

    added = inventory.add(portion)

    assert added
    assert inventory.items == (portion,)
    assert inventory.total_nutrition == 5


def test_inventory_rejects_item_when_full() -> None:
    inventory = Inventory(capacity=1)
    first = FoodPortion(
        source_id=1,
        nutrition=5,
    )
    second = FoodPortion(
        source_id=2,
        nutrition=10,
    )

    assert inventory.add(first)
    assert not inventory.add(second)
    assert inventory.items == (first,)


def test_inventory_removes_item() -> None:
    inventory = Inventory(capacity=1)
    portion = FoodPortion(
        source_id=1,
        nutrition=5,
    )
    inventory.add(portion)

    removed = inventory.remove(portion)

    assert removed
    assert inventory.is_empty


def test_inventory_returns_false_for_unknown_item() -> None:
    inventory = Inventory(capacity=1)
    portion = FoodPortion(
        source_id=1,
        nutrition=5,
    )

    assert not inventory.remove(portion)


def test_inventory_clear_returns_removed_items() -> None:
    inventory = Inventory(capacity=2)
    first = FoodPortion(
        source_id=1,
        nutrition=5,
    )
    second = FoodPortion(
        source_id=2,
        nutrition=10,
    )
    inventory.add(first)
    inventory.add(second)

    removed = inventory.clear()

    assert removed == (
        first,
        second,
    )
    assert inventory.is_empty


def test_inventory_rejects_negative_capacity() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        Inventory(capacity=-1)


def test_food_portion_rejects_invalid_nutrition() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        FoodPortion(
            source_id=1,
            nutrition=0,
        )