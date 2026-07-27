import pytest

from ant_colony.entities.entity import Entity


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