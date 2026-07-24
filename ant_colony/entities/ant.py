#ant_colony/entities/ant.py
import math
import random

from ant_colony.components.inventory import Inventory
from ant_colony.components.senses import Senses
from ant_colony.components.state import AntState
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Polygon, Shape
from ant_colony.knowledge import Knowledge

class Ant(Entity):
    def __init__(self, ant_id: int) -> None:
        x = random.uniform(
            0,
            settings.WORLD_WIDTH,
        )

        y = random.uniform(
            0,
            settings.SCREEN_HEIGHT,
        )

        super().__init__(
            entity_id=ant_id,
            x=x,
            y=y,
            discoverable_radius=settings.ANT_DISCOVERABLE_RADIUS,
        )

        self.speed = random.uniform(
            settings.ANT_MIN_SPEED,
            settings.ANT_MAX_SPEED,
        )

        self.heading = random.uniform(
            0,
            360,
        )

        self.state = AntState.WANDERING
        self.senses = Senses()
        self.inventory = Inventory()
        self.knowledge = Knowledge()

    def update(self) -> None:
        if self.state == AntState.WANDERING:
            self.wander()

    def wander(self) -> None:
        heading_radians = math.radians(self.heading)

        self.x += math.cos(heading_radians) * self.speed
        self.y += math.sin(heading_radians) * self.speed

        self.heading += random.uniform(
            -settings.ANT_TURN_SPEED,
            settings.ANT_TURN_SPEED,
        )

        self.wrap_position()

    def wrap_position(self) -> None:
        if self.x < 0:
            self.x = settings.WORLD_WIDTH
        elif self.x > settings.WORLD_WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = settings.SCREEN_HEIGHT
        elif self.y > settings.SCREEN_HEIGHT:
            self.y = 0

    def shapes(self) -> tuple[Shape, ...]:
        heading_radians = math.radians(self.heading)

        front = (
            self.x
            + math.cos(heading_radians) * settings.ANT_DRAW_LENGTH,
            self.y
            + math.sin(heading_radians) * settings.ANT_DRAW_LENGTH,
        )

        left = (
            self.x
            + math.cos(heading_radians + 2.5) * settings.ANT_DRAW_WIDTH,
            self.y
            + math.sin(heading_radians + 2.5) * settings.ANT_DRAW_WIDTH,
        )

        right = (
            self.x
            + math.cos(heading_radians - 2.5) * settings.ANT_DRAW_WIDTH,
            self.y
            + math.sin(heading_radians - 2.5) * settings.ANT_DRAW_WIDTH,
        )

        return (
            Polygon(
                points=(front, left, right),
                color=settings.ANT_COLOR,
            ),
        )