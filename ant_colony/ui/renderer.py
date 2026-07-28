import logging
from importlib.resources import as_file, files

import pygame

from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.graphics.camera import Camera
from ant_colony.graphics.primitives import (
    Circle,
    Ellipse,
    Polygon,
    Shape,
)
from ant_colony.ui.window_layout import WindowLayout
from ant_colony.world import World

logger = logging.getLogger(__name__)
PACKAGE_NAME = "ant_colony"
WORLD_BACKGROUND_ASSET = "assets/backgrounds/old-growth-forest-map.png"
ANT_WORKER_ASSET = "assets/ants/meadow-ant-worker-2x2.png"
ANT_WORKER_NATIVE_HEADING = -90


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        camera: Camera,
    ) -> None:
        self.screen = screen
        self.camera = camera
        self.world_background = self._load_world_background()
        self.ant_worker_sprite = self._load_ant_worker_sprite()
        self._scaled_background = self.world_background
        self._scaled_background_size = self.world_background.get_size()
        self._world_clip_rect = pygame.Rect(
            0, 0, settings.WORLD_WIDTH, settings.WORLD_HEIGHT
        )
        self.show_grid = False
        self.show_hitboxes = False
        self.show_radius_overlays = False
        if not pygame.font.get_init():
            pygame.font.init()
        self.debug_font = pygame.font.SysFont(None, 18)

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
        background = self._background_for(layout.world_viewport.size)
        self.screen.blit(background, layout.world_viewport.topleft)
        cursor_screen = self._cursor_screen_position()
        cursor_world: tuple[float, float] | None
        if cursor_screen is None:
            cursor_world = None
            hovered_entity = None
        else:
            cursor_world = self.camera.screen_to_world(*cursor_screen)
            hovered_entity = world.entity_under_position(cursor_world)

        self.screen.set_clip(self._world_clip_rect)

        if self.show_grid:
            self._draw_grid()

        for entity in world.entities:
            self._draw_entity(entity)

        if self.show_hitboxes:
            self._draw_hitboxes(world)
        if self.show_radius_overlays and hovered_entity is not None:
            self._draw_hovered_radii(hovered_entity)

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
            self.show_radius_overlays = not self.show_radius_overlays

    def _draw_entity(self, entity: Entity) -> None:
        if isinstance(entity, Ant) and self.ant_worker_sprite is not None:
            self._draw_ant(entity)
            return

        for shape in entity.shapes():
            self._draw_shape(shape)

    def _draw_ant(self, ant: Ant) -> None:
        if self.ant_worker_sprite is None:
            return

        source_width, source_height = self.ant_worker_sprite.get_size()
        target_height = self.camera.scale_length(settings.ANT_SPRITE_HEIGHT)
        target_width = max(
            1,
            round(target_height * source_width / source_height),
        )
        scaled_sprite = pygame.transform.smoothscale(
            self.ant_worker_sprite,
            (target_width, target_height),
        )
        rotated_sprite = pygame.transform.rotate(
            scaled_sprite,
            ANT_WORKER_NATIVE_HEADING - ant.heading,
        )
        center = self.camera.world_to_screen(
            ant.x,
            ant.y,
        )
        destination = rotated_sprite.get_rect(
            center=center,
        )
        self.screen.blit(
            rotated_sprite,
            destination,
        )

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
        points = [self.camera.world_to_screen(x, y) for x, y in polygon.points]

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
            radius=(settings.ANT_RADIUS + settings.SELECTION_RING_PADDING),
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

    def _draw_hovered_radii(self, entity: Entity) -> None:
        self._draw_circle(
            Circle(
                x=entity.x,
                y=entity.y,
                radius=entity.discoverable_radius,
                color=settings.DEBUG_DISCOVERY_RADIUS_COLOR,
                width=2,
            )
        )

        if isinstance(entity, Ant):
            self._draw_circle(
                Circle(
                    x=entity.x,
                    y=entity.y,
                    radius=entity.senses.radius,
                    color=settings.DEBUG_SENSE_RADIUS_COLOR,
                    width=2,
                )
            )

    def _draw_coordinate_overlay(
        self,
        cursor_world: tuple[float, float],
    ) -> None:
        cursor_label = f"cursor: ({int(cursor_world[0])}, {int(cursor_world[1])})"
        self._draw_debug_text(
            cursor_label,
            self._world_clip_rect.left + 10,
            self._world_clip_rect.bottom - 24,
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
                screen_x + 2,
                screen_y + 2,
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
                screen_x + 2,
                screen_y + 2,
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
        return self._mouse_is_focused() and self._world_clip_rect.collidepoint(
            cursor_screen
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

    def _background_for(
        self,
        size: tuple[int, int],
    ) -> pygame.Surface:
        if size != self._scaled_background_size:
            self._scaled_background = pygame.transform.smoothscale(
                self.world_background,
                size,
            )
            self._scaled_background_size = size
        return self._scaled_background

    @staticmethod
    def _load_world_background() -> pygame.Surface:
        background_resource = files(PACKAGE_NAME).joinpath(WORLD_BACKGROUND_ASSET)
        attempted_location = f"{PACKAGE_NAME}/{WORLD_BACKGROUND_ASSET}"
        try:
            with as_file(background_resource) as background_path:
                background = pygame.image.load(str(background_path))
        except (
            FileNotFoundError,
            pygame.error,
        ) as error:
            logger.warning(
                "Failed to load world background from %s: %s",
                attempted_location,
                error,
            )
            fallback = pygame.Surface(
                (
                    settings.WORLD_WIDTH,
                    settings.WORLD_HEIGHT,
                )
            )
            fallback.fill(settings.BACKGROUND_COLOR)
            return fallback

        target_size = (
            settings.WORLD_WIDTH,
            settings.WORLD_HEIGHT,
        )
        if background.get_size() == target_size:
            return background

        return pygame.transform.scale(background, target_size)

    @staticmethod
    def _load_ant_worker_sprite() -> pygame.Surface | None:
        sprite_resource = files(PACKAGE_NAME).joinpath(ANT_WORKER_ASSET)
        attempted_location = f"{PACKAGE_NAME}/{ANT_WORKER_ASSET}"
        try:
            with as_file(sprite_resource) as sprite_path:
                return pygame.image.load(str(sprite_path))
        except (
            FileNotFoundError,
            pygame.error,
        ) as error:
            logger.warning(
                "Failed to load ant worker sprite from %s: %s",
                attempted_location,
                error,
            )
            return None
