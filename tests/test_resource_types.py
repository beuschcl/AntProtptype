from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.food import Food
from ant_colony.graphics.primitives import Polygon


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