#ant_colony/entities/nest.py
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

    def shapes(self) -> tuple[Shape, ...]:
        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=settings.NEST_RADIUS,
                color=settings.NEST_COLOR,
            ),
        )