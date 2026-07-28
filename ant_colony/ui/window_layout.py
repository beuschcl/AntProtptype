from __future__ import annotations

from dataclasses import dataclass

import pygame

from ant_colony.config import settings


@dataclass(frozen=True)
class WindowLayout:
    window_rect: pygame.Rect
    world_area: pygame.Rect
    world_viewport: pygame.Rect
    inspector_rect: pygame.Rect
    divider_rect: pygame.Rect

    @classmethod
    def calculate(
        cls,
        window_size: tuple[int, int],
        inspector_width: int,
    ) -> WindowLayout:
        width, height = window_size
        max_inspector_width = min(
            settings.MAX_INSPECTOR_WIDTH,
            width - settings.MIN_WORLD_VIEWPORT_WIDTH,
        )
        inspector_width = max(
            settings.MIN_INSPECTOR_WIDTH,
            min(inspector_width, max_inspector_width),
        )
        divider_x = width - inspector_width
        world_area = pygame.Rect(0, 0, divider_x, height)

        scale = min(
            world_area.width / settings.WORLD_WIDTH,
            world_area.height / settings.WORLD_HEIGHT,
        )
        viewport_width = round(settings.WORLD_WIDTH * scale)
        viewport_height = round(settings.WORLD_HEIGHT * scale)
        world_viewport = pygame.Rect(
            (world_area.width - viewport_width) // 2,
            (world_area.height - viewport_height) // 2,
            viewport_width,
            viewport_height,
        )

        return cls(
            window_rect=pygame.Rect(0, 0, width, height),
            world_area=world_area,
            world_viewport=world_viewport,
            inspector_rect=pygame.Rect(
                divider_x + settings.INSPECTOR_DIVIDER_WIDTH,
                0,
                inspector_width - settings.INSPECTOR_DIVIDER_WIDTH,
                height,
            ),
            divider_rect=pygame.Rect(
                divider_x,
                0,
                settings.INSPECTOR_DIVIDER_WIDTH,
                height,
            ),
        )


class WindowController:
    def __init__(self) -> None:
        self.inspector_width = settings.INSPECTOR_WIDTH
        self.windowed_size = (
            settings.SCREEN_WIDTH,
            settings.SCREEN_HEIGHT,
        )
        self.fullscreen = False
        self.dragging_divider = False

    def create_screen(self) -> pygame.Surface:
        return pygame.display.set_mode(
            self.windowed_size,
            pygame.RESIZABLE,
        )

    def toggle_fullscreen(self) -> pygame.Surface:
        if self.fullscreen:
            self.fullscreen = False
            return pygame.display.set_mode(
                self.windowed_size,
                pygame.RESIZABLE,
            )

        current = pygame.display.get_surface()
        if current is not None:
            self.windowed_size = current.get_size()
        self.fullscreen = True
        return pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN,
        )

    def layout(self, screen: pygame.Surface) -> WindowLayout:
        return WindowLayout.calculate(
            screen.get_size(),
            self.inspector_width,
        )

    def handle_divider_event(
        self,
        event: pygame.event.Event,
        layout: WindowLayout,
    ) -> bool:
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and layout.divider_rect.inflate(8, 0).collidepoint(event.pos)
        ):
            self.dragging_divider = True
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.dragging_divider
            self.dragging_divider = False
            return was_dragging
        if event.type == pygame.MOUSEMOTION and self.dragging_divider:
            requested_width = layout.window_rect.width - event.pos[0]
            self.inspector_width = max(
                settings.MIN_INSPECTOR_WIDTH,
                min(
                    requested_width,
                    settings.MAX_INSPECTOR_WIDTH,
                    layout.window_rect.width - settings.MIN_WORLD_VIEWPORT_WIDTH,
                ),
            )
            return True
        return False
