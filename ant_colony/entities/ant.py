#ant_colony/entities/ant.py
import math
import random

from ant_colony.components.inventory import Inventory
from ant_colony.components.state import AntState
from ant_colony.config import settings
from ant_colony.knowledge.knowledge import Knowledge


class Ant:

    def __init__(self, ant_id):

        self.id = ant_id

        self.x = random.randint(
            0,
            settings.SCREEN_WIDTH,
        )

        self.y = random.randint(
            0,
            settings.SCREEN_HEIGHT,
        )

        self.speed = random.uniform(
            settings.MIN_SPEED,
            settings.MAX_SPEED,
        )

        self.heading = random.uniform(
            0,
            360,
        )

        self.state = AntState.WANDERING

        self.inventory = Inventory()
        self.knowledge = Knowledge()

    def update(self):

        if self.state == AntState.WANDERING:
            self.wander()

    def wander(self):

        radians = math.radians(
            self.heading
        )

        self.x += (
            math.cos(radians)
            * self.speed
        )

        self.y += (
            math.sin(radians)
            * self.speed
        )

        self.heading += random.uniform(
            -settings.TURN_SPEED,
            settings.TURN_SPEED,
        )

        self.wrap_position()

    def wrap_position(self):

        if self.x < 0:
            self.x = settings.SCREEN_WIDTH

        elif self.x > settings.SCREEN_WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = settings.SCREEN_HEIGHT

        elif self.y > settings.SCREEN_HEIGHT:
            self.y = 0