import pytest

from ant_colony.components import (
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.food import Food


def make_food(
    quantity: int = 2,
) -> Food:
    return Food(
        food_id=7,
        x=100,
        y=200,
        nutrition=5,
        quantity=quantity,
    )


def test_food_stores_quantity() -> None:
    food = make_food(quantity=2)

    assert food.quantity == 2
    assert not food.is_depleted


def test_food_collect_returns_portion() -> None:
    food = make_food(quantity=2)

    portion = food.collect()

    assert portion == ResourcePortion(
        source_id=7,
        resource_type=ResourceType.FOOD,
        value=5,
    )
    assert food.quantity == 1


def test_food_becomes_depleted() -> None:
    food = make_food(quantity=1)

    food.collect()

    assert food.is_depleted
    assert food.quantity == 0
    assert food.shapes() == ()


def test_depleted_food_cannot_be_collected() -> None:
    food = make_food(quantity=1)
    food.collect()

    assert food.collect() is None
    assert food.quantity == 0


def test_undiscovered_food_discoverable_radius_grows_over_time() -> None:
    food = make_food()
    initial_radius = food.discoverable_radius

    food.update()

    assert food.discoverable_radius == pytest.approx(
        initial_radius
        + settings.FOOD_DISCOVERABLE_RADIUS_GROWTH_PER_TICK
    )


def test_discovered_food_discoverable_radius_stops_growing() -> None:
    food = make_food()
    food.update()
    grown_radius = food.discoverable_radius

    food.mark_discovered()
    food.update()

    assert food.is_discovered
    assert food.discoverable_radius == grown_radius


def test_food_discoverable_radius_is_capped() -> None:
    food = make_food()
    food.discoverable_radius = settings.FOOD_DISCOVERABLE_RADIUS_MAX

    food.update()

    assert food.discoverable_radius == settings.FOOD_DISCOVERABLE_RADIUS_MAX


@pytest.mark.parametrize(
    ("nutrition", "quantity"),
    [
        (0, 1),
        (-1, 1),
        (5, 0),
        (5, -1),
    ],
)
def test_food_rejects_invalid_values(
    nutrition: int,
    quantity: int,
) -> None:
    with pytest.raises(ValueError):
        Food(
            food_id=1,
            x=0,
            y=0,
            nutrition=nutrition,
            quantity=quantity,
        )
