import pytest

from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.building_material import (
    BuildingMaterial,
)
from ant_colony.entities.food import Food
from ant_colony.entities.water import Water
from ant_colony.graphics.primitives import Ellipse, Polygon


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
    fill_shape, outline_shape = food.shapes()

    assert isinstance(fill_shape, Polygon)
    assert fill_shape.points == (
        (100, 90),
        (110, 100),
        (100, 110),
        (90, 100),
    )
    assert fill_shape.color == settings.FOOD_COLOR
    assert outline_shape.width == 2
    assert outline_shape.color == settings.FOOD_OUTLINE_COLOR


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
    outer_shape, inner_shape = water.shapes()

    assert isinstance(outer_shape, Ellipse)
    assert isinstance(inner_shape, Ellipse)
    assert outer_shape.radius_x == 12
    assert outer_shape.radius_y == pytest.approx(8.4)
    assert outer_shape.width == 3
    assert outer_shape.color == settings.WATER_COLOR
    assert inner_shape.radius_x == pytest.approx(7.8)
    assert inner_shape.radius_y == pytest.approx(5.4)
    assert inner_shape.width == 2
    assert inner_shape.color == settings.WATER_COLOR
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
    fill_shape, outline_shape = material.shapes()

    assert isinstance(fill_shape, Polygon)
    assert fill_shape.points == (
        (91, 91),
        (109, 91),
        (109, 109),
        (91, 109),
    )
    assert fill_shape.color == settings.BUILDING_MATERIAL_COLOR
    assert outline_shape.width == 2
    assert (
        outline_shape.color
        == settings.BUILDING_MATERIAL_OUTLINE_COLOR
    )
    portion = material.collect()

    assert portion is not None
    assert (
        portion.resource_type
        is ResourceType.BUILDING_MATERIAL
    )