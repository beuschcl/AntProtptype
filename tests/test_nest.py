from ant_colony.components import FoodPortion
from ant_colony.entities.nest import Nest


def test_nest_starts_with_empty_food_reserve() -> None:
    nest = Nest(x=100, y=100)

    assert nest.food_reserve == 0
    assert nest.delivered_portions == 0


def test_nest_deposits_food_portions() -> None:
    nest = Nest(x=100, y=100)

    deposited_nutrition = nest.deposit(
        (
            FoodPortion(
                source_id=1,
                nutrition=5,
            ),
            FoodPortion(
                source_id=2,
                nutrition=3,
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
            FoodPortion(
                source_id=1,
                nutrition=5,
            ),
        )
    )
    nest.deposit(
        (
            FoodPortion(
                source_id=2,
                nutrition=3,
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