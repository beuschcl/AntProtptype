#ant_colony/entities/nest.py
from ant_colony.config import settings
from ant_colony.entities.entity import Entity


class Nest(Entity):

    def __init__(self, x, y):

        super().__init__(
            "nest",
            x,
            y,
            settings.NEST_DISCOVERABLE_RADIUS,
        )