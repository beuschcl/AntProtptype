#ant_colony/entities/food.py
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle, Shape


class Food(Entity):
    def __init__(
        self,
        food_id: int,
        x: float,
        y: float,
        nutrition: int,
    ) -> None:
        super().__init__(
            food_id,
            x,
            y,
            settings.FOOD_DISCOVERABLE_RADIUS,
        )

        self.nutrition = nutrition

    def shapes(self) -> tuple[Shape, ...]:
        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=settings.FOOD_RADIUS,
                color=settings.FOOD_COLOR,
            ),
        )