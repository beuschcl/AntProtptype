#ant_colony/world.py
from ant_colony.entities.ant import Ant
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest

from ant_colony.config import settings


class World:

    def __init__(self):

        self.nest = Nest(
            settings.SCREEN_WIDTH // 2,
            settings.SCREEN_HEIGHT // 2,
        )

        self.ants = []

        for ant_id in range(settings.STARTING_ANTS):
            self.ants.append(
                Ant(ant_id)
            )

        self.food = [
            Food(
                200,
                200,
                nutrition=5,
            )
        ]

    def update(self):
        pass

    def __repr__(self):

        return (
            f"World("
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}"
            f")"
        )