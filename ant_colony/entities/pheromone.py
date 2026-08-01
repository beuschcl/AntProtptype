from enum import Enum

from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle, Shape


class PheromoneType(Enum):
    EXPLORE = "explore"
    FOOD = "food"
    AVOID = "avoid"


class Pheromone(Entity):
    def __init__(
        self,
        pheromone_id: int,
        x: float,
        y: float,
        source_food_id: int | None = None,
        pheromone_type: PheromoneType = PheromoneType.FOOD,
        strength: float = settings.PHEROMONE_INITIAL_STRENGTH,
    ) -> None:
        if strength <= 0:
            raise ValueError(
                "Pheromone strength must be greater than zero."
            )
        if pheromone_type == PheromoneType.FOOD and source_food_id is None:
            raise ValueError(
                "Food pheromones must track a source food id."
            )

        super().__init__(
            entity_id=pheromone_id,
            x=x,
            y=y,
            discoverable_radius=(
                settings.PHEROMONE_DISCOVERABLE_RADIUS
            ),
        )

        self._strength = strength
        self._source_food_id = source_food_id
        self._pheromone_type = pheromone_type

    @property
    def strength(self) -> float:
        return self._strength

    @property
    def source_food_id(self) -> int | None:
        return self._source_food_id

    @property
    def pheromone_type(self) -> PheromoneType:
        return self._pheromone_type

    @property
    def is_depleted(self) -> bool:
        return self._strength <= 0

    @property
    def hitbox_radius(self) -> float:
        return settings.PHEROMONE_RADIUS * self._strength

    def update(self) -> None:
        self._strength = max(
            0,
            self._strength
            - settings.PHEROMONE_EVAPORATION_RATE,
        )

    def shapes(self) -> tuple[Shape, ...]:
        if self.is_depleted:
            return ()

        radius = (
            settings.PHEROMONE_RADIUS
            * self._strength
        )

        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=radius,
                color=self._color,
            ),
        )

    @property
    def _color(self) -> tuple[int, int, int]:
        if self._pheromone_type == PheromoneType.EXPLORE:
            return settings.EXPLORE_PHEROMONE_COLOR
        if self._pheromone_type == PheromoneType.AVOID:
            return settings.AVOID_PHEROMONE_COLOR
        return settings.FOOD_PHEROMONE_COLOR
