import pytest

from ant_colony.components.senses import Senses
from ant_colony.entities.entity import Entity


def make_entity(
    entity_id: int,
    x: float,
    y: float,
    discoverable_radius: float = 0,
) -> Entity:
    return Entity(
        entity_id=entity_id,
        x=x,
        y=y,
        discoverable_radius=(
            discoverable_radius
        ),
    )


def test_senses_detect_entity_inside_range() -> None:
    senses = Senses(radius=10)
    observer = make_entity(
        entity_id=1,
        x=0,
        y=0,
    )
    target = make_entity(
        entity_id=2,
        x=6,
        y=8,
    )

    assert senses.can_detect(
        observer,
        target,
    )


def test_senses_do_not_detect_entity_outside_range() -> None:
    senses = Senses(radius=9)
    observer = make_entity(
        entity_id=1,
        x=0,
        y=0,
    )
    target = make_entity(
        entity_id=2,
        x=6,
        y=8,
    )

    assert not senses.can_detect(
        observer,
        target,
    )


def test_target_discoverable_radius_extends_detection() -> None:
    senses = Senses(radius=8)
    observer = make_entity(
        entity_id=1,
        x=0,
        y=0,
    )
    target = make_entity(
        entity_id=2,
        x=6,
        y=8,
        discoverable_radius=2,
    )

    assert senses.can_detect(
        observer,
        target,
    )


def test_senses_do_not_detect_observer_itself() -> None:
    senses = Senses(radius=10)
    observer = make_entity(
        entity_id=1,
        x=0,
        y=0,
    )

    assert not senses.can_detect(
        observer,
        observer,
    )


def test_detect_returns_only_nearby_entities() -> None:
    senses = Senses(radius=10)
    observer = make_entity(
        entity_id=1,
        x=0,
        y=0,
    )
    nearby = make_entity(
        entity_id=2,
        x=5,
        y=0,
    )
    distant = make_entity(
        entity_id=3,
        x=20,
        y=0,
    )

    detected = senses.detect(
        observer,
        [
            observer,
            nearby,
            distant,
        ],
    )

    assert detected == (nearby,)


def test_senses_reject_negative_radius() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        Senses(radius=-1)