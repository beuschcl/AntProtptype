#ant_colony/entities/food.py
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle


class Food(Entity):

    def __init__(self, food_id, x, y, nutrition):

        super().__init__(
            food_id,
            x,
            y,
            settings.FOOD_DISCOVERABLE_RADIUS,
        )

        self.nutrition = nutrition

    def shapes(self):

        return [
            Circle(
                self.x,
                self.y,
                settings.FOOD_RADIUS,
                (0, 100, 255),
            )
        ]