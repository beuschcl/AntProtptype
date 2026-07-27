import math
from collections.abc import Iterable

from ant_colony.components import (
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Polygon, Shape


class Nest(Entity):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            entity_id="nest",
            x=x,
            y=y,
            discoverable_radius=(
                settings.NEST_DISCOVERABLE_RADIUS
            ),
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
        portions: Iterable[ResourcePortion],
    ) -> int:
        deposited_portions = tuple(portions)

        invalid_portions = tuple(
            portion
            for portion in deposited_portions
            if portion.resource_type
            != ResourceType.FOOD
        )

        if invalid_portions:
            raise ValueError(
                "The food reserve only accepts food portions."
            )

        nutrition = sum(
            portion.value
            for portion in deposited_portions
        )

        self._food_reserve += nutrition
        self._delivered_portions += len(
            deposited_portions
        )

        return nutrition

    @property
    def hitbox_radius(self) -> float:
        return settings.NEST_RADIUS

    def shapes(self) -> tuple[Shape, ...]:
        points = tuple(
            (
                self.x
                + math.cos(math.radians(angle))
                * settings.NEST_RADIUS,
                self.y
                + math.sin(math.radians(angle))
                * settings.NEST_RADIUS,
            )
            for angle in range(0, 360, 60)
        )

        return (
            Polygon(
                points=points,
                color=settings.NEST_COLOR,
                width=3,
            ),
        )