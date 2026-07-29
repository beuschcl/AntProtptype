#ant_colony/graphics/renderer.py

import pygame

from ant_colony.config import settings
from ant_colony.graphics.primitives import Circle, Polygon


class Renderer:

    def __init__(self, screen, camera):

        self.screen = screen
        self.camera = camera

    def draw(self, world):

        self.screen.fill(
            settings.BACKGROUND_COLOR
        )

        self.draw_entities(world)

        pygame.display.flip()

    def draw_entities(self, world):

        entities = [
            world.nest,
            *world.food,
            *world.ants,
        ]

        for entity in entities:

            for shape in entity.shapes():

                if isinstance(shape, Circle):

                    x, y = self.camera.world_to_screen(
                        shape.x,
                        shape.y,
                    )

                    pygame.draw.circle(
                        self.screen,
                        shape.color,
                        (x, y),
                        int(shape.radius),
                    )

                elif isinstance(shape, Polygon):

                    points = [
                        self.camera.world_to_screen(
                            x,
                            y,
                        )
                        for x, y in shape.points
                    ]

                    pygame.draw.polygon(
                        self.screen,
                        shape.color,
                        points,
                    )

            if entity is world.selected_ant:

                x, y = self.camera.world_to_screen(
                    entity.x,
                    entity.y,
                )

                pygame.draw.circle(
                    self.screen,
                    settings.SELECTION_COLOR,
                    (x, y),
                    settings.ANT_RADIUS
                    + settings.SELECTION_RING_PADDING,
                    settings.SELECTION_RING_WIDTH,
                )