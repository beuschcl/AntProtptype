from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle, Shape


class Pheromone(Entity):
    def __init__(
        self,
        pheromone_id: int,
        x: float,
        y: float,
        strength: float = settings.PHEROMONE_INITIAL_STRENGTH,
    ) -> None:
        if strength <= 0:
            raise ValueError(
                "Pheromone strength must be greater than zero."
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

    @property
    def strength(self) -> float:
        return self._strength

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
                color=settings.PHEROMONE_COLOR,
            ),
        )