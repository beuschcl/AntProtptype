#ant_colony/entities/ant.py
import math
import random
import pygame

from ant_colony.components.inventory import Inventory
from ant_colony.components.senses import Senses
from ant_colony.components.state import AntState
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.knowledge.knowledge import Knowledge


class Ant(Entity):

    def __init__(self, ant_id):

        x = random.randint(
            0,
            settings.SCREEN_WIDTH,
        )

        y = random.randint(
            0,
            settings.SCREEN_HEIGHT,
        )

        super().__init__(
            ant_id,
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
            -settings.ANT_TURN_SPEED,
            settings.ANT_TURN_SPEED,
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

    def draw(self, screen):

        angle = math.radians(self.heading)

        front = (
            self.x + math.cos(angle) * 12,
            self.y + math.sin(angle) * 12,
        )

        left = (
            self.x + math.cos(angle + 2.5) * 8,
            self.y + math.sin(angle + 2.5) * 8,
        )

        right = (
            self.x + math.cos(angle - 2.5) * 8,
            self.y + math.sin(angle - 2.5) * 8,
        )

        pygame.draw.polygon(
            screen,
            (255, 255, 255),
            [
                front,
                left,
                right,
            ],
        )