from contextlib import contextmanager
from pathlib import Path
from tempfile import gettempdir
from types import SimpleNamespace

import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui import renderer as renderer_module
from ant_colony.world import World


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

    class FakeTraversable:
        def __init__(self) -> None:
            self.joinpath_argument = ""

        def joinpath(self, value: str) -> "FakeTraversable":
            self.joinpath_argument = value
            return self

    fake_resource = FakeTraversable()

    def fake_files(package: str) -> FakeTraversable:
        calls["package"] = package
        return fake_resource

    @contextmanager
    def fake_as_file(_: object):
        yield Path(gettempdir()) / "old-growth-forest-map.png"

    monkeypatch.setattr(pygame.image, "load", fake_load)
    monkeypatch.setattr(pygame.transform, "scale", fake_scale)
    monkeypatch.setattr(renderer_module, "files", fake_files)
    monkeypatch.setattr(
        renderer_module,
        "as_file",
        fake_as_file,
    )

    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())

    assert calls["package"] == "ant_colony"
    assert (
        fake_resource.joinpath_argument
        == renderer_module.WORLD_BACKGROUND_ASSET
    )
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
        entity_under_position=lambda _: None,
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


def test_renderer_toggles_grid_and_hitboxes() -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())

    renderer.handle_event(
        pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_g,
        )
    )
    renderer.handle_event(
        pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_h,
        )
    )

    assert renderer.show_grid
    assert renderer.show_hitboxes


def test_renderer_debug_overlays_stay_in_world_viewport(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_grid = True
    renderer.show_hitboxes = True
    world = World()
    ant = world.ants[0]
    ant.x = 100
    ant.y = 100

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))

    renderer.draw(world)

    assert (
        screen.get_at((settings.WORLD_WIDTH + 20, 20))[:3]
        == settings.BACKGROUND_COLOR
    )


def test_renderer_does_not_mutate_world_state(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_hitboxes = True
    world = World()
    ant = world.ants[0]
    ant.x = 100
    ant.y = 100
    before = repr(world)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))

    renderer.draw(world)

    assert repr(world) == before


def test_renderer_draws_only_hovered_ant_sense_radius(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_hitboxes = True
    world = World()
    first_ant = world.ants[0]
    second_ant = world.ants[1]
    first_ant.x = 100
    first_ant.y = 100
    second_ant.x = 300
    second_ant.y = 300

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    captured_circles: list[renderer_module.Circle] = []

    original_draw_circle = renderer._draw_circle

    def capture_circle(circle: renderer_module.Circle) -> None:
        captured_circles.append(circle)
        original_draw_circle(circle)

    monkeypatch.setattr(renderer, "_draw_circle", capture_circle)

    renderer.draw(world)

    sense_rings = [
        circle
        for circle in captured_circles
        if (
            circle.color == settings.DEBUG_SENSE_RADIUS_COLOR
            and circle.radius == settings.ANT_SENSE_RADIUS
        )
    ]

    assert len(sense_rings) == 1
