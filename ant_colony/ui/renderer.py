import pygame

from ant_colony.config import settings


class Renderer:

    def __init__(self, screen):

        self.screen = screen

    def draw(self, world):

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.draw_nest(world)
        self.draw_food(world)
        self.draw_ants(world)

        pygame.display.flip()

    def draw_nest(self, world):

        pygame.draw.circle(
            self.screen,
            (150, 75, 0),
            (
                int(world.nest.x),
                int(world.nest.y),
            ),
            20,
        )

    def draw_food(self, world):

        for food in world.food:

            pygame.draw.circle(
                self.screen,
                (0, 100, 255),
                (
                    int(food.x),
                    int(food.y),
                ),
                settings.FOOD_RADIUS,
            )

    def draw_ants(self, world):

        for ant in world.ants:

            ant.draw(self.screen)

            if ant is world.selected_ant:
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 0),
                    (
                        int(ant.x),
                        int(ant.y),
                    ),
                    settings.ANT_RADIUS + 6,
                    2,
                )