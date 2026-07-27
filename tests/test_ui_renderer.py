from pathlib import Path
from types import SimpleNamespace

import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui import renderer as renderer_module


def test_renderer_loads_and_scales_world_background_once(
    monkeypatch,
) -> None:
    loaded_surface = pygame.Surface((12, 12))
    scaled_surface = pygame.Surface(
        (settings.WORLD_WIDTH, settings.SCREEN_HEIGHT)
    )
    calls: dict[str, object] = {}

    def fake_load(path: str) -> pygame.Surface:
        calls["path"] = path
        return loaded_surface

    def fake_scale(
        surface: pygame.Surface,
        size: tuple[int, int],
    ) -> pygame.Surface:
        calls["surface"] = surface
        calls["size"] = size
        return scaled_surface

    monkeypatch.setattr(pygame.image, "load", fake_load)
    monkeypatch.setattr(pygame.transform, "scale", fake_scale)

    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())

    assert Path(calls["path"]).name == Path(
        renderer_module.WORLD_BACKGROUND_ASSET
    ).name
    assert Path(calls["path"]).is_absolute()
    assert calls["surface"] is loaded_surface
    assert calls["size"] == (
        settings.WORLD_WIDTH,
        settings.SCREEN_HEIGHT,
    )
    assert renderer.world_background is scaled_surface


def test_renderer_draws_background_only_in_world_viewport(
    monkeypatch,
) -> None:
    world_background_color = (11, 22, 33)
    background = pygame.Surface(
        (settings.WORLD_WIDTH, settings.SCREEN_HEIGHT)
    )
    background.fill(world_background_color)

    monkeypatch.setattr(
        renderer_module.Renderer,
        "_load_world_background",
        staticmethod(lambda: background),
    )

    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    world = SimpleNamespace(
        entities=(),
        selected_ant=None,
    )

    renderer.draw(world)

    assert screen.get_at((10, 10))[:3] == world_background_color
    assert (
        screen.get_at((settings.WORLD_WIDTH + 10, 10))[:3]
        == settings.BACKGROUND_COLOR
    )
    assert (
        screen.get_at((settings.WORLD_WIDTH, 10))[:3]
        == settings.INSPECTOR_DIVIDER_COLOR
    )


def test_renderer_uses_fallback_when_background_load_fails(
    monkeypatch,
) -> None:
    def raise_file_not_found(_: str) -> pygame.Surface:
        raise FileNotFoundError

    monkeypatch.setattr(
        pygame.image,
        "load",
        raise_file_not_found,
    )

    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())

    assert renderer.world_background.get_size() == (
        settings.WORLD_WIDTH,
        settings.SCREEN_HEIGHT,
    )
    assert renderer.world_background.get_at((0, 0))[:3] == (
        settings.BACKGROUND_COLOR
    )
