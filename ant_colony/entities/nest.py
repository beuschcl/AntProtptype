from collections.abc import Iterable

from ant_colony.components import FoodPortion
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle, Shape


class Nest(Entity):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            entity_id="nest",
            x=x,
            y=y,
            discoverable_radius=settings.NEST_DISCOVERABLE_RADIUS,
        )

        self._food_reserve = 0
        self._delivered_portions = 0

    @property
    def food_reserve(self) -> int:
        return self._food_reserve

    @property
    def delivered_portions(self) -> int:
        return self._delivered_portions

    def deposit(
        self,
        portions: Iterable[FoodPortion],
    ) -> int:
        deposited_portions = tuple(portions)

        nutrition = sum(
            portion.nutrition
            for portion in deposited_portions
        )

        self._food_reserve += nutrition
        self._delivered_portions += len(
            deposited_portions
        )

        return nutrition

    def shapes(self) -> tuple[Shape, ...]:
        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=settings.NEST_RADIUS,
                color=settings.NEST_COLOR,
            ),
        )