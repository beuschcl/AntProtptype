import pygame

from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.camera import Camera
from ant_colony.graphics.primitives import Circle, Polygon, Shape
from ant_colony.world import World


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        camera: Camera,
    ) -> None:
        self.screen = screen
        self.camera = camera

    def draw(self, world: World) -> None:
        self.screen.fill(settings.BACKGROUND_COLOR)

        for entity in world.entities:
            self._draw_entity(entity)

        if world.selected_ant is not None:
            self._draw_selection_ring(world.selected_ant)

        self._draw_inspector_divider()

    def _draw_entity(self, entity: Entity) -> None:
        for shape in entity.shapes():
            self._draw_shape(shape)

    def _draw_shape(self, shape: Shape) -> None:
        match shape:
            case Circle():
                self._draw_circle(shape)

            case Polygon():
                self._draw_polygon(shape)

    def _draw_circle(self, circle: Circle) -> None:
        center = self.camera.world_to_screen(
            circle.x,
            circle.y,
        )

        radius = self.camera.scale_length(circle.radius)

        pygame.draw.circle(
            self.screen,
            circle.color,
            center,
            radius,
            circle.width,
        )

    def _draw_polygon(self, polygon: Polygon) -> None:
        points = [
            self.camera.world_to_screen(x, y)
            for x, y in polygon.points
        ]

        pygame.draw.polygon(
            self.screen,
            polygon.color,
            points,
            polygon.width,
        )

    def _draw_selection_ring(self, entity: Entity) -> None:
        selection_ring = Circle(
            x=entity.x,
            y=entity.y,
            radius=(
                settings.ANT_RADIUS
                + settings.SELECTION_RING_PADDING
            ),
            color=settings.SELECTION_COLOR,
            width=settings.SELECTION_RING_WIDTH,
        )

        self._draw_circle(selection_ring)

    def _draw_inspector_divider(self) -> None:
        pygame.draw.line(
            self.screen,
            settings.INSPECTOR_DIVIDER_COLOR,
            (settings.WORLD_WIDTH, 0),
            (settings.WORLD_WIDTH, settings.SCREEN_HEIGHT),
        )