import pytest

from ant_colony.components import (
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.nest import Nest
from ant_colony.graphics.primitives import Polygon


def test_nest_starts_with_empty_food_reserve() -> None:
    nest = Nest(x=100, y=100)

    assert nest.food_reserve == 0
    assert nest.delivered_portions == 0
    shape = nest.shapes()[0]

    assert isinstance(shape, Polygon)
    assert shape.width == 3
    assert len(shape.points) == 6
    assert shape.points[0] == pytest.approx(
        (100 + settings.NEST_RADIUS, 100)
    )


def test_nest_deposits_food_portions() -> None:
    nest = Nest(x=100, y=100)

    deposited_nutrition = nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=5,
            ),
            ResourcePortion(
                source_id=2,
                resource_type=ResourceType.FOOD,
                value=3,
            ),
        )
    )

    assert deposited_nutrition == 8
    assert nest.food_reserve == 8
    assert nest.delivered_portions == 2


def test_nest_accumulates_multiple_deposits() -> None:
    nest = Nest(x=100, y=100)

    nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=5,
            ),
        )
    )
    nest.deposit(
        (
            ResourcePortion(
                source_id=2,
                resource_type=ResourceType.FOOD,
                value=3,
            ),
        )
    )

    assert nest.food_reserve == 8
    assert nest.delivered_portions == 2


def test_empty_deposit_does_not_change_reserve() -> None:
    nest = Nest(x=100, y=100)

    deposited_nutrition = nest.deposit(())

    assert deposited_nutrition == 0
    assert nest.food_reserve == 0
    assert nest.delivered_portions == 0


def test_nest_rejects_non_food_portions() -> None:
    nest = Nest(x=100, y=100)

    with pytest.raises(
        ValueError,
        match="only accepts food portions",
    ):
        nest.deposit(
            (
                ResourcePortion(
                    source_id=1,
                    resource_type=ResourceType.WATER,
                    value=5,
                ),
            )
        )