import pytest

from ant_colony.config import settings
from ant_colony.entities.pheromone import Pheromone, PheromoneType
from ant_colony.graphics.primitives import Circle


def test_pheromone_starts_with_configured_strength() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        x=100,
        y=200,
    )

    assert (
        pheromone.strength
        == settings.PHEROMONE_INITIAL_STRENGTH
    )
    assert not pheromone.is_depleted


def test_pheromone_rejects_nonpositive_strength() -> None:
    with pytest.raises(
        ValueError,
        match="strength must be greater than zero",
    ):
        Pheromone(
            pheromone_id=1,
            source_food_id=7,
            x=100,
            y=200,
            strength=0,
        )


def test_pheromone_evaporates() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        x=100,
        y=200,
        strength=0.5,
    )

    pheromone.update()

    assert pheromone.strength == pytest.approx(
        0.5 - settings.PHEROMONE_EVAPORATION_RATE
    )


def test_pheromone_strength_cannot_be_negative() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        x=100,
        y=200,
        strength=(
            settings.PHEROMONE_EVAPORATION_RATE / 2
        ),
    )

    pheromone.update()

    assert pheromone.strength == 0
    assert pheromone.is_depleted


def test_depleted_pheromone_has_no_shapes() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        x=100,
        y=200,
        strength=(
            settings.PHEROMONE_EVAPORATION_RATE / 2
        ),
    )

    pheromone.update()

    assert pheromone.shapes() == ()


def test_pheromone_exposes_circle_shape() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        x=100,
        y=200,
    )

    shapes = pheromone.shapes()

    assert len(shapes) == 1
    assert isinstance(shapes[0], Circle)
    assert shapes[0].x == 100
    assert shapes[0].y == 200
    assert shapes[0].color == settings.PHEROMONE_COLOR


def test_pheromone_tracks_source_food() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=17,
        x=100,
        y=200,
    )

    assert pheromone.source_food_id == 17


def test_food_pheromone_requires_source_food() -> None:
    with pytest.raises(
        ValueError,
        match="source food id",
    ):
        Pheromone(
            pheromone_id=1,
            pheromone_type=PheromoneType.FOOD,
            x=100,
            y=200,
        )


def test_explore_pheromone_does_not_require_source_food() -> None:
    pheromone = Pheromone(
        pheromone_id=1,
        pheromone_type=PheromoneType.EXPLORE,
        x=100,
        y=200,
    )

    assert pheromone.source_food_id is None
    assert pheromone.pheromone_type == PheromoneType.EXPLORE


def test_pheromone_color_depends_on_type() -> None:
    food = Pheromone(
        pheromone_id=1,
        source_food_id=7,
        pheromone_type=PheromoneType.FOOD,
        x=100,
        y=200,
    )
    explore = Pheromone(
        pheromone_id=2,
        pheromone_type=PheromoneType.EXPLORE,
        x=100,
        y=200,
    )
    avoid = Pheromone(
        pheromone_id=3,
        pheromone_type=PheromoneType.AVOID,
        x=100,
        y=200,
    )

    assert food.shapes()[0].color == settings.FOOD_PHEROMONE_COLOR
    assert explore.shapes()[0].color == settings.EXPLORE_PHEROMONE_COLOR
    assert avoid.shapes()[0].color == settings.AVOID_PHEROMONE_COLOR
