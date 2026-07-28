import pytest

from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food


def test_entity_calculates_distance_to_another_entity() -> None:
    first = Entity(
        entity_id=1,
        x=0,
        y=0,
        discoverable_radius=0,
    )

    second = Entity(
        entity_id=2,
        x=3,
        y=4,
        discoverable_radius=0,
    )

    assert first.distance_to(second) == pytest.approx(5)


def test_entity_calculates_distance_to_position() -> None:
    entity = Entity(
        entity_id=1,
        x=0,
        y=0,
        discoverable_radius=0,
    )

    assert entity.distance_to_position(3, 4) == pytest.approx(5)


def test_entity_exposes_hitbox_radius() -> None:
    food = Food(
        food_id=1,
        x=0,
        y=0,
        nutrition=1,
    )

    assert food.hitbox_radius == 10


def test_intersection_allows_combined_hitbox_boundary() -> None:
    ant = Ant(ant_id=1)
    food = Food(
        food_id=1,
        x=0,
        y=0,
        nutrition=1,
    )

    ant.x = 0
    ant.y = 0
    food.x = ant.hitbox_radius + food.hitbox_radius
    food.y = 0

    assert ant.intersects_entity(food)