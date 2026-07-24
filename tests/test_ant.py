from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.graphics.primitives import Polygon
from ant_colony.entities.food import Food
from ant_colony.knowledge import (
    EntityObservation,
)

def test_ant_starts_inside_world_bounds() -> None:
    ant = Ant(ant_id=1)

    assert 0 <= ant.x <= settings.WORLD_WIDTH
    assert 0 <= ant.y <= settings.SCREEN_HEIGHT


def test_ant_wraps_past_right_world_boundary() -> None:
    ant = Ant(ant_id=1)
    ant.x = settings.WORLD_WIDTH + 1

    ant.wrap_position()

    assert ant.x == 0


def test_ant_wraps_past_left_world_boundary() -> None:
    ant = Ant(ant_id=1)
    ant.x = -1

    ant.wrap_position()

    assert ant.x == settings.WORLD_WIDTH


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
        food = Food(
            food_id=7,
            x=200,
            y=200,
            nutrition=5,
        )

        observation = ant.observe(food)

        assert observation == EntityObservation(
            entity_id=7,
            entity_type="food",
            x=200,
            y=200,
        )

        assert ant.knowledge.recall("entity:food:7") == observation

    def test_observing_entity_again_updates_position() -> None:
        ant = Ant(ant_id=1)
        food = Food(
            food_id=7,
            x=200,
            y=200,
            nutrition=5,
        )

        ant.observe(food)

        food.x = 250
        food.y = 300

        ant.observe(food)

        observation = ant.knowledge.recall("entity:food:7")

        assert isinstance(
            observation,
            EntityObservation,
        )
        assert observation.position == (
            250,
            300,
        )
        assert ant.knowledge.count() == 1