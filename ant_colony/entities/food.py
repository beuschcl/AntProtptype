from ant_colony.components import FoodPortion
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
        quantity: int = 1,
    ) -> None:
        if nutrition <= 0:
            raise ValueError(
                "Food nutrition must be greater than zero."
            )

        if quantity <= 0:
            raise ValueError(
                "Food quantity must be greater than zero."
            )

        super().__init__(
            entity_id=food_id,
            x=x,
            y=y,
            discoverable_radius=(
                settings.FOOD_DISCOVERABLE_RADIUS
            ),
        )

        self.nutrition = nutrition
        self._quantity = quantity

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def is_depleted(self) -> bool:
        return self._quantity == 0

    def collect(self) -> FoodPortion | None:
        if self.is_depleted:
            return None

        self._quantity -= 1

        return FoodPortion(
            source_id=self.id,
            nutrition=self.nutrition,
        )

    def shapes(self) -> tuple[Shape, ...]:
        if self.is_depleted:
            return ()

        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=settings.FOOD_RADIUS,
                color=settings.FOOD_COLOR,
            ),
        )