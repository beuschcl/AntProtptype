#ant_colony/world.py
import math
import pygame

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
        self.selected_ant = None
        self.food = [
            Food(
                1,
                200,
                200,
                nutrition=5,
            )
        ]

    def update(self):

        for ant in self.ants:
            ant.update()

    def __repr__(self):

        return (
            f"World("
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}"
            f")"
        )

    def handle_click(self, position):

        mouse_x, mouse_y = position

        self.selected_ant = None

        closest_ant = None
        closest_distance = settings.CLICK_RADIUS

        for ant in self.ants:

            distance = math.hypot(
                ant.x - mouse_x,
                ant.y - mouse_y,
            )

            if distance < closest_distance:
                closest_ant = ant
                closest_distance = distance

        self.selected_ant = closest_ant

    def draw(self, screen):

        for ant in self.ants:
            ant.draw(screen)

        for food in self.food:
            food.draw(screen)

        self.nest.draw(screen)

        if self.selected_ant:
            pygame.draw.circle(
                screen,
                (255, 255, 0),
                (
                    int(self.selected_ant.x),
                    int(self.selected_ant.y),
                ),
                15,
                2,
            )