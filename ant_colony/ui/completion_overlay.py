from __future__ import annotations

import pygame

from ant_colony.config import settings
from ant_colony.ui.window_layout import WindowLayout


class CompletionOverlay:
    """Semi-transparent modal shown when the colony reaches MAX_ANTS.

    Call ``draw()`` once per frame when ``world.is_complete`` is True,
    then call ``handle_event()`` for each pygame event to receive
    ``"restart"`` or ``"exit"`` actions.  The domain is never called
    from here; only pygame display surfaces are touched.
    """

    def __init__(self) -> None:
        if not pygame.font.get_init():
            pygame.font.init()
        self._font_title = pygame.font.SysFont(
            None,
            settings.COMPLETION_TITLE_FONT_SIZE,
        )
        self._font_message = pygame.font.SysFont(
            None,
            settings.COMPLETION_MESSAGE_FONT_SIZE,
        )
        self._font_button = pygame.font.SysFont(
            None,
            settings.COMPLETION_BUTTON_FONT_SIZE,
        )
        self._restart_rect: pygame.Rect | None = None
        self._exit_rect: pygame.Rect | None = None

    def draw(
        self,
        screen: pygame.Surface,
        layout: WindowLayout,
    ) -> None:
        """Draw the completion overlay onto *screen* inside the world viewport."""
        viewport = layout.world_viewport
        cx = viewport.centerx
        cy = viewport.centery

        # Semi-transparent dark panel over the world viewport.
        overlay = pygame.Surface(viewport.size, pygame.SRCALPHA)
        overlay.fill(settings.COMPLETION_OVERLAY_FILL_COLOR)
        screen.blit(overlay, viewport.topleft)

        # Title
        title_surf = self._font_title.render(
            "Colony Complete!",
            True,
            settings.COMPLETION_TITLE_COLOR,
        )
        screen.blit(
            title_surf,
            title_surf.get_rect(
                centerx=cx,
                centery=cy - settings.COMPLETION_TITLE_Y_OFFSET,
            ),
        )

        # Subtitle
        msg_surf = self._font_message.render(
            f"Your colony reached {settings.MAX_ANTS} ants!",
            True,
            settings.COMPLETION_MESSAGE_COLOR,
        )
        screen.blit(
            msg_surf,
            msg_surf.get_rect(
                centerx=cx,
                centery=cy - settings.COMPLETION_MESSAGE_Y_OFFSET,
            ),
        )

        # Buttons
        restart_label = self._font_button.render(
            "Start Over",
            True,
            settings.COMPLETION_BUTTON_TEXT_COLOR,
        )
        exit_label = self._font_button.render(
            "Exit Game",
            True,
            settings.COMPLETION_BUTTON_TEXT_COLOR,
        )

        btn_w = max(restart_label.get_width(), exit_label.get_width())
        btn_h = restart_label.get_height()
        total_w = btn_w * 2 + settings.COMPLETION_BUTTON_GAP
        left = cx - total_w // 2
        btn_y = cy + settings.COMPLETION_BUTTON_Y_OFFSET

        self._restart_rect = pygame.Rect(
            left,
            btn_y,
            btn_w + settings.COMPLETION_BUTTON_PADDING_X * 2,
            btn_h + settings.COMPLETION_BUTTON_PADDING_Y * 2,
        )
        self._exit_rect = pygame.Rect(
            left
            + btn_w
            + settings.COMPLETION_BUTTON_PADDING_X * 2
            + settings.COMPLETION_BUTTON_GAP,
            btn_y,
            btn_w + settings.COMPLETION_BUTTON_PADDING_X * 2,
            btn_h + settings.COMPLETION_BUTTON_PADDING_Y * 2,
        )

        pygame.draw.rect(
            screen,
            settings.COMPLETION_BUTTON_COLOR,
            self._restart_rect,
            border_radius=settings.COMPLETION_BUTTON_BORDER_RADIUS,
        )
        pygame.draw.rect(
            screen,
            settings.COMPLETION_BUTTON_COLOR,
            self._exit_rect,
            border_radius=settings.COMPLETION_BUTTON_BORDER_RADIUS,
        )

        screen.blit(
            restart_label,
            restart_label.get_rect(center=self._restart_rect.center),
        )
        screen.blit(
            exit_label,
            exit_label.get_rect(center=self._exit_rect.center),
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Return ``"restart"``, ``"exit"``, or ``None`` for the given event."""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        pos = event.pos
        if self._restart_rect is not None and self._restart_rect.collidepoint(pos):
            return "restart"
        if self._exit_rect is not None and self._exit_rect.collidepoint(pos):
            return "exit"
        return None