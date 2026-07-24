from ant_colony.components import ResourceType
from ant_colony.entities.building_material import (
    BuildingMaterial,
)
from ant_colony.entities.food import Food
from ant_colony.entities.water import Water


def test_food_configuration() -> None:
    food = Food(
        food_id=1,
        x=100,
        y=100,
        nutrition=5,
        quantity=2,
    )

    assert food.resource_type is ResourceType.FOOD
    assert food.nutrition == 5


def test_water_configuration() -> None:
    water = Water(
        water_id=1,
        x=100,
        y=100,
        hydration=4,
        quantity=2,
    )

    assert water.resource_type is ResourceType.WATER
    assert water.hydration == 4
    portion = water.collect()

    assert portion is not None
    assert portion.resource_type is ResourceType.WATER


def test_building_material_configuration() -> None:
    material = BuildingMaterial(
        material_id=1,
        x=100,
        y=100,
        construction_value=3,
        quantity=2,
    )

    assert (
        material.resource_type
        is ResourceType.BUILDING_MATERIAL
    )
    assert material.construction_value == 3
    portion = material.collect()

    assert portion is not None
    assert (
        portion.resource_type
        is ResourceType.BUILDING_MATERIAL
    )