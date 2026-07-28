import pygame

from ant_colony.config import settings
from ant_colony.ui.window_layout import WindowController, WindowLayout


def test_layout_preserves_world_aspect_ratio() -> None:
    layout = WindowLayout.calculate((1600, 900), 300)

    assert (
        abs(
            layout.world_viewport.width / layout.world_viewport.height
            - settings.WORLD_WIDTH / settings.WORLD_HEIGHT
        )
        < 0.002
    )
    assert layout.world_viewport.center == layout.world_area.center
    assert layout.world_viewport.right <= layout.world_area.right
    assert layout.world_viewport.bottom <= layout.world_area.bottom


def test_layout_clamps_inspector_width() -> None:
    narrow = WindowLayout.calculate((800, 500), 999)
    wide = WindowLayout.calculate((1600, 900), 1)

    assert narrow.inspector_rect.width + settings.INSPECTOR_DIVIDER_WIDTH == 400
    assert wide.inspector_rect.width + settings.INSPECTOR_DIVIDER_WIDTH == (
        settings.MIN_INSPECTOR_WIDTH
    )


def test_divider_drag_resizes_inspector_with_limits() -> None:
    controller = WindowController()
    layout = WindowLayout.calculate((1300, 700), controller.inspector_width)
    down = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=layout.divider_rect.center,
    )

    assert controller.handle_divider_event(down, layout)
    controller.handle_divider_event(
        pygame.event.Event(
            pygame.MOUSEMOTION,
            pos=(1200, 100),
            rel=(0, 0),
            buttons=(1, 0, 0),
        ),
        layout,
    )
    assert controller.inspector_width == settings.MIN_INSPECTOR_WIDTH

    controller.handle_divider_event(
        pygame.event.Event(
            pygame.MOUSEMOTION,
            pos=(500, 100),
            rel=(0, 0),
            buttons=(1, 0, 0),
        ),
        layout,
    )
    assert controller.inspector_width == settings.MAX_INSPECTOR_WIDTH


def test_fullscreen_toggle_restores_windowed_size(monkeypatch) -> None:
    controller = WindowController()
    windowed = pygame.Surface((1111, 777))
    fullscreen = pygame.Surface((1920, 1080))
    restored = pygame.Surface((1111, 777))
    surfaces = iter((fullscreen, restored))
    calls: list[tuple[tuple[int, int], int]] = []

    monkeypatch.setattr(pygame.display, "get_surface", lambda: windowed)

    def fake_set_mode(
        size: tuple[int, int],
        flags: int,
    ) -> pygame.Surface:
        calls.append((size, flags))
        return next(surfaces)

    monkeypatch.setattr(pygame.display, "set_mode", fake_set_mode)

    assert controller.toggle_fullscreen() is fullscreen
    assert controller.fullscreen
    assert controller.windowed_size == (1111, 777)
    assert controller.toggle_fullscreen() is restored
    assert not controller.fullscreen
    assert calls == [
        ((0, 0), pygame.FULLSCREEN),
        ((1111, 777), pygame.RESIZABLE),
    ]
