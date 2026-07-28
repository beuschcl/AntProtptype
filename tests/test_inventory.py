import pytest

from ant_colony.components import (
    Inventory,
    ResourcePortion,
    ResourceType,
)


def test_inventory_starts_empty() -> None:
    inventory = Inventory(capacity=2)

    assert inventory.items == ()
    assert inventory.is_empty
    assert not inventory.is_full
    assert inventory.count() == 0


def test_inventory_adds_resource_portion() -> None:
    inventory = Inventory(capacity=2)
    portion = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.FOOD,
        value=5,
    )

    added = inventory.add(portion)

    assert added
    assert inventory.items == (portion,)
    assert inventory.total_value == 5


def test_inventory_rejects_item_when_full() -> None:
    inventory = Inventory(capacity=1)
    first = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.FOOD,
        value=5,
    )
    second = ResourcePortion(
        source_id=2,
        resource_type=ResourceType.FOOD,
        value=10,
    )

    assert inventory.add(first)
    assert not inventory.add(second)
    assert inventory.items == (first,)


def test_inventory_removes_item() -> None:
    inventory = Inventory(capacity=1)
    portion = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.FOOD,
        value=5,
    )
    inventory.add(portion)

    removed = inventory.remove(portion)

    assert removed
    assert inventory.is_empty


def test_inventory_returns_false_for_unknown_item() -> None:
    inventory = Inventory(capacity=1)
    portion = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.FOOD,
        value=5,
    )

    assert not inventory.remove(portion)


def test_inventory_clear_returns_removed_items() -> None:
    inventory = Inventory(capacity=2)
    first = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.FOOD,
        value=5,
    )
    second = ResourcePortion(
        source_id=2,
        resource_type=ResourceType.FOOD,
        value=10,
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


def test_resource_portion_rejects_invalid_value() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=0,
        )


def test_inventory_adds_multiple_resource_types() -> None:
    inventory = Inventory(capacity=2)
    water_portion = ResourcePortion(
        source_id=1,
        resource_type=ResourceType.WATER,
        value=3,
    )
    building_material_portion = ResourcePortion(
        source_id=2,
        resource_type=ResourceType.BUILDING_MATERIAL,
        value=4,
    )

    assert inventory.add(water_portion)
    assert inventory.add(building_material_portion)
    assert inventory.items == (
        water_portion,
        building_material_portion,
    )
