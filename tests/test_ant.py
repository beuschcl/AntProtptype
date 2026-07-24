from ant_colony.components import (
    AntState,
    FoodPortion,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.graphics.primitives import Polygon
from ant_colony.knowledge import EntityObservation


def make_food(
    x: float = 200,
    y: float = 200,
    quantity: int = 1,
) -> Food:
    return Food(
        food_id=7,
        x=x,
        y=y,
        nutrition=5,
        quantity=quantity,
    )


def test_ant_starts_inside_world_bounds() -> None:
    ant = Ant(ant_id=1)

    assert 0 <= ant.x <= settings.WORLD_WIDTH
    assert 0 <= ant.y <= settings.SCREEN_HEIGHT


def test_ant_starts_wandering() -> None:
    ant = Ant(ant_id=1)

    assert ant.state == AntState.WANDERING


def test_ant_exposes_polygon_shape() -> None:
    ant = Ant(ant_id=1)

    shapes = ant.shapes()

    assert len(shapes) == 1
    assert isinstance(shapes[0], Polygon)


def test_ant_owns_independent_knowledge() -> None:
    first_ant = Ant(ant_id=1)
    second_ant = Ant(ant_id=2)

    first_ant.knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert first_ant.knowledge.recall(
        "food_location"
    ) == (200, 200)

    assert second_ant.knowledge.recall(
        "food_location"
    ) is None


def test_ant_observes_entity() -> None:
    ant = Ant(ant_id=1)
    food = make_food()

    observation = ant.observe(food)

    assert observation == EntityObservation(
        entity_id=7,
        entity_type="food",
        x=200,
        y=200,
    )

    assert ant.knowledge.recall(
        "entity:food:7"
    ) == observation


def test_observing_entity_again_updates_position() -> None:
    ant = Ant(ant_id=1)
    food = make_food()

    ant.observe(food)

    food.x = 250
    food.y = 300

    ant.observe(food)

    observation = ant.knowledge.recall(
        "entity:food:7"
    )

    assert isinstance(
        observation,
        EntityObservation,
    )
    assert observation.position == (
        250,
        300,
    )
    assert ant.knowledge.count() == 1


def test_ant_selects_food_target() -> None:
    ant = Ant(ant_id=1)
    food = make_food()

    selected = ant.select_food_target(food)

    assert selected
    assert ant.food_target is food
    assert ant.state == AntState.SEEKING_FOOD


def test_ant_moves_toward_food_target() -> None:
    ant = Ant(ant_id=1)
    food = make_food(
        x=100,
        y=0,
    )
    ant.x = 0
    ant.y = 0
    ant.speed = 2
    ant.select_food_target(food)

    ant.update()

    assert ant.x == 2
    assert ant.y == 0


def test_ant_collects_food_in_range() -> None:
    ant = Ant(ant_id=1)
    food = make_food(
        x=100,
        y=100,
    )
    ant.x = 100
    ant.y = 100
    ant.select_food_target(food)

    collected = ant.collect_from(food)

    assert collected
    assert ant.inventory.count() == 1
    assert food.is_depleted
    assert ant.food_target is None
    assert ant.state == AntState.CARRYING_FOOD


def test_ant_cannot_collect_distant_food() -> None:
    ant = Ant(ant_id=1)
    food = make_food(
        x=500,
        y=500,
    )
    ant.x = 0
    ant.y = 0

    assert not ant.collect_from(food)
    assert ant.inventory.is_empty
    assert not food.is_depleted


def test_ant_with_full_inventory_rejects_target() -> None:
    ant = Ant(ant_id=1)
    first_food = make_food()
    second_food = Food(
        food_id=8,
        x=250,
        y=250,
        nutrition=5,
    )

    ant.x = first_food.x
    ant.y = first_food.y
    ant.collect_from(first_food)

    selected = ant.select_food_target(
        second_food
    )

    assert not selected
    assert ant.food_target is None

def test_ant_can_select_nest_when_carrying_food() -> None:
    ant = Ant(ant_id=1)
    nest = Nest(x=100, y=100)

    ant.inventory.add(
        FoodPortion(
            source_id=1,
            nutrition=5,
        )
    )

    selected = ant.select_nest_target(nest)

    assert selected is True
    assert ant.nest_target is nest
    assert ant.state == AntState.CARRYING_FOOD


def test_ant_cannot_select_nest_with_empty_inventory() -> None:
    ant = Ant(ant_id=1)
    nest = Nest(x=100, y=100)

    selected = ant.select_nest_target(nest)

    assert selected is False
    assert ant.nest_target is None


def test_ant_moves_toward_nest() -> None:
    ant = Ant(ant_id=1)
    nest = Nest(x=110, y=100)

    ant.x = 100
    ant.y = 100
    ant.speed = 2

    ant.inventory.add(
        FoodPortion(
            source_id=1,
            nutrition=5,
        )
    )
    ant.select_nest_target(nest)

    ant.update()

    assert ant.x == 102
    assert ant.y == 100


def test_ant_deposits_inventory_into_nest() -> None:
    ant = Ant(ant_id=1)
    nest = Nest(x=100, y=100)

    ant.x = 100
    ant.y = 100

    ant.inventory.add(
        FoodPortion(
            source_id=1,
            nutrition=5,
        )
    )
    ant.select_nest_target(nest)

    deposited_nutrition = ant.deposit_into(nest)

    assert deposited_nutrition == 5
    assert ant.inventory.is_empty
    assert nest.food_reserve == 5
    assert ant.nest_target is None
    assert ant.state == AntState.WANDERING


def test_ant_cannot_deposit_when_too_far_from_nest() -> None:
    ant = Ant(ant_id=1)
    nest = Nest(x=500, y=500)

    ant.x = 100
    ant.y = 100

    portion = FoodPortion(
        source_id=1,
        nutrition=5,
    )
    ant.inventory.add(portion)
    ant.select_nest_target(nest)

    deposited_nutrition = ant.deposit_into(nest)

    assert deposited_nutrition == 0
    assert ant.inventory.items == (portion,)
    assert nest.food_reserve == 0