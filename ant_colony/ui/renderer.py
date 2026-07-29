import pygame

from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.entities.pheromone import Pheromone
from ant_colony.graphics.camera import Camera
from ant_colony.graphics.primitives import (
    Circle,
    Ellipse,
    Polygon,
    Shape,
)
from ant_colony.ui.window_layout import WindowLayout
from ant_colony.world import World


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        camera: Camera,
    ) -> None:
        self.screen = screen
        self.camera = camera
        self._world_clip_rect = pygame.Rect(
            0, 0, settings.WORLD_WIDTH, settings.WORLD_HEIGHT
        )
        self.show_grid = False
        self.show_hitboxes = False
        self.show_radius_overlays = False
        if not pygame.font.get_init():
            pygame.font.init()
        self.debug_font = pygame.font.SysFont(None, settings.DEBUG_FONT_SIZE)

    def set_screen(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def draw(
        self,
        world: World,
        layout: WindowLayout | None = None,
    ) -> None:
        if layout is None:
            layout = WindowLayout.calculate(
                self.screen.get_size(),
                settings.INSPECTOR_WIDTH,
            )
        self._world_clip_rect = layout.world_viewport
        self.camera.fit(
            layout.world_viewport,
            (settings.WORLD_WIDTH, settings.WORLD_HEIGHT),
        )
        self.screen.fill(settings.BACKGROUND_COLOR)
        pygame.draw.rect(
            self.screen,
            settings.BACKGROUND_COLOR,
            layout.world_viewport,
        )
        self._draw_world_bounds(layout)
        cursor_screen = self._cursor_screen_position()
        cursor_world: tuple[float, float] | None
        if cursor_screen is None:
            cursor_world = None
        else:
            cursor_world = self.camera.screen_to_world(
                *cursor_screen
            )

        self.screen.set_clip(self._world_clip_rect)

        if self.show_grid:
            self._draw_grid()

        for entity in world.entities:
            self._draw_entity(entity)

        if self.show_hitboxes:
            self._draw_hitboxes(world)
            self._draw_obstacle_bounds(world)
        if self.show_radius_overlays:
            self._draw_radius_overlays(world)

        if world.selected_ant is not None:
            self._draw_selection_ring(world.selected_ant)

        if (
            self.show_grid
            and cursor_screen is not None
            and cursor_world is not None
            and self._should_show_cursor_coordinates(cursor_screen)
        ):
            self._draw_coordinate_overlay(
                cursor_world,
            )

        self.screen.set_clip(None)
        self._draw_inspector_divider(layout)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_g:
            self.show_grid = not self.show_grid
        elif event.key == pygame.K_h:
            self.show_hitboxes = not self.show_hitboxes
        elif event.key == pygame.K_r:
            self.show_radius_overlays = (
                not self.show_radius_overlays
            )

    def _draw_entity(self, entity: Entity) -> None:
        for shape in entity.shapes():
            self._draw_shape(shape)

    def _draw_shape(self, shape: Shape) -> None:
        match shape:
            case Circle():
                self._draw_circle(shape)

            case Ellipse():
                self._draw_ellipse(shape)

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

    def _draw_ellipse(self, ellipse: Ellipse) -> None:
        center_x, center_y = self.camera.world_to_screen(
            ellipse.x,
            ellipse.y,
        )
        radius_x = self.camera.scale_length(ellipse.radius_x)
        radius_y = self.camera.scale_length(ellipse.radius_y)
        rect = pygame.Rect(
            center_x - radius_x,
            center_y - radius_y,
            radius_x * 2,
            radius_y * 2,
        )
        pygame.draw.ellipse(
            self.screen,
            ellipse.color,
            rect,
            ellipse.width,
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

    def _draw_grid(self) -> None:
        for x in range(
            0,
            settings.WORLD_WIDTH + 1,
            settings.DEBUG_GRID_SPACING,
        ):
            screen_x, _ = self.camera.world_to_screen(x, 0)
            pygame.draw.line(
                self.screen,
                settings.DEBUG_GRID_COLOR,
                (screen_x, self._world_clip_rect.top),
                (screen_x, self._world_clip_rect.bottom),
            )

        for y in range(
            0,
            settings.WORLD_HEIGHT + 1,
            settings.DEBUG_GRID_SPACING,
        ):
            _, screen_y = self.camera.world_to_screen(0, y)
            pygame.draw.line(
                self.screen,
                settings.DEBUG_GRID_COLOR,
                (self._world_clip_rect.left, screen_y),
                (self._world_clip_rect.right, screen_y),
            )

    def _draw_hitboxes(self, world: World) -> None:
        for entity in world.entities:
            if entity.hitbox_radius <= 0:
                continue

            self._draw_circle(
                Circle(
                    x=entity.x,
                    y=entity.y,
                    radius=entity.hitbox_radius,
                    color=settings.DEBUG_HITBOX_COLOR,
                    width=settings.DEBUG_HITBOX_WIDTH,
                )
            )

    def _draw_obstacle_bounds(self, world: World) -> None:
        for obstacle in world.obstacles:
            left, top = self.camera.world_to_screen(
                obstacle.left,
                obstacle.top,
            )
            right, bottom = self.camera.world_to_screen(
                obstacle.right,
                obstacle.bottom,
            )
            rect = pygame.Rect(
                min(left, right),
                min(top, bottom),
                abs(right - left),
                abs(bottom - top),
            )
            pygame.draw.rect(
                self.screen,
                settings.DEBUG_OBSTACLE_COLOR,
                rect,
                settings.DEBUG_OBSTACLE_WIDTH,
            )

    def _draw_radius_overlays(self, world: World) -> None:
        for entity in world.entities:
            self._draw_discovery_radius(entity)

            if isinstance(entity, Ant):
                self._draw_ant_sense_radius(entity)
                self._draw_ant_interaction_radius(entity)

    def _draw_discovery_radius(self, entity: Entity) -> None:
        if entity.discoverable_radius <= 0:
            return

        self._draw_circle(
            Circle(
                x=entity.x,
                y=entity.y,
                radius=entity.discoverable_radius,
                color=self._discovery_radius_color(entity),
                width=settings.DEBUG_RADIUS_OVERLAY_WIDTH,
            )
        )

    def _draw_ant_sense_radius(self, ant: Ant) -> None:
        self._draw_circle(
            Circle(
                x=ant.x,
                y=ant.y,
                radius=ant.senses.radius,
                color=settings.DEBUG_SENSE_RADIUS_COLOR,
                width=settings.DEBUG_RADIUS_OVERLAY_WIDTH,
            )
        )

    def _draw_ant_interaction_radius(self, ant: Ant) -> None:
        self._draw_circle(
            Circle(
                x=ant.x,
                y=ant.y,
                radius=ant.hitbox_radius + settings.ANT_INTERACTION_RADIUS,
                color=settings.DEBUG_INTERACTION_RADIUS_COLOR,
                width=settings.DEBUG_RADIUS_OVERLAY_WIDTH,
            )
        )

    @staticmethod
    def _discovery_radius_color(entity: Entity) -> tuple[int, int, int]:
        if isinstance(entity, Ant):
            return settings.DEBUG_ANT_DISCOVERY_RADIUS_COLOR
        if isinstance(entity, Food):
            return settings.DEBUG_FOOD_DISCOVERY_RADIUS_COLOR
        if isinstance(entity, Nest):
            return settings.DEBUG_NEST_DISCOVERY_RADIUS_COLOR
        if isinstance(entity, Pheromone):
            return settings.DEBUG_PHEROMONE_DISCOVERY_RADIUS_COLOR
        return settings.DEBUG_DISCOVERY_RADIUS_COLOR

    def _draw_coordinate_overlay(
        self,
        cursor_world: tuple[float, float],
    ) -> None:
        cursor_label = (
            f"cursor: ({int(cursor_world[0])}, "
            f"{int(cursor_world[1])})"
        )
        self._draw_debug_text(
            cursor_label,
            self._world_clip_rect.left + settings.DEBUG_CURSOR_LABEL_MARGIN_X,
            self._world_clip_rect.bottom
            - settings.DEBUG_CURSOR_LABEL_BOTTOM_OFFSET,
        )

        for x in range(
            settings.DEBUG_GRID_SPACING,
            settings.WORLD_WIDTH,
            settings.DEBUG_GRID_SPACING * 2,
        ):
            screen_x, screen_y = self.camera.world_to_screen(
                x,
                0,
            )
            self._draw_debug_text(
                str(x),
                screen_x + settings.DEBUG_COORDINATE_LABEL_OFFSET,
                screen_y + settings.DEBUG_COORDINATE_LABEL_OFFSET,
            )

        for y in range(
            settings.DEBUG_GRID_SPACING,
            settings.WORLD_HEIGHT,
            settings.DEBUG_GRID_SPACING * 2,
        ):
            screen_x, screen_y = self.camera.world_to_screen(
                0,
                y,
            )
            self._draw_debug_text(
                str(y),
                screen_x + settings.DEBUG_COORDINATE_LABEL_OFFSET,
                screen_y + settings.DEBUG_COORDINATE_LABEL_OFFSET,
            )

    def _draw_debug_text(
        self,
        text: str,
        x: int,
        y: int,
    ) -> None:
        label = self.debug_font.render(
            text,
            True,
            settings.DEBUG_TEXT_COLOR,
        )
        self.screen.blit(label, (x, y))

    @staticmethod
    def _cursor_screen_position() -> tuple[int, int] | None:
        try:
            return pygame.mouse.get_pos()
        except pygame.error:
            # Raised in headless/uninitialized video contexts.
            return None

    def _should_show_cursor_coordinates(
        self,
        cursor_screen: tuple[int, int],
    ) -> bool:
        return (
            self._mouse_is_focused()
            and self._world_clip_rect.collidepoint(cursor_screen)
        )

    @staticmethod
    def _mouse_is_focused() -> bool:
        try:
            return bool(pygame.mouse.get_focused())
        except pygame.error:
            return False

    def _draw_inspector_divider(
        self,
        layout: WindowLayout,
    ) -> None:
        pygame.draw.rect(
            self.screen,
            settings.INSPECTOR_DIVIDER_COLOR,
            layout.divider_rect,
        )

    def _draw_world_bounds(
        self,
        layout: WindowLayout,
    ) -> None:
        pygame.draw.rect(
            self.screen,
            settings.SCOPE_BOUNDARY_COLOR,
            layout.world_viewport,
            width=settings.WORLD_BOUNDS_WIDTH,
        )