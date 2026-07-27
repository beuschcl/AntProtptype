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


def test_renderer_toggles_grid_hitboxes_and_radii_independently() -> None:
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
    renderer.handle_event(
        pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_r,
        )
    )

    assert renderer.show_grid
    assert renderer.show_hitboxes
    assert renderer.show_radius_overlays

    renderer.handle_event(
        pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_h,
        )
    )
    assert renderer.show_grid
    assert not renderer.show_hitboxes
    assert renderer.show_radius_overlays


def test_renderer_draws_camera_transformed_grid_lines(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    camera = Camera()
    camera.x = 50
    camera.y = 25
    camera.zoom = 2
    renderer = renderer_module.Renderer(screen, camera)
    lines: list[tuple[tuple[int, int], tuple[int, int]]] = []

    def capture_line(
        _surface: pygame.Surface,
        _color: tuple[int, int, int],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        lines.append((start, end))

    monkeypatch.setattr(pygame.draw, "line", capture_line)

    renderer._draw_grid()

    expected_x, _ = camera.world_to_screen(100, 0)
    _, expected_y = camera.world_to_screen(0, 100)
    assert any(
        start == (expected_x, 0)
        and end == (expected_x, settings.SCREEN_HEIGHT)
        for start, end in lines
    )
    assert any(
        start == (0, expected_y)
        and end == (settings.SCREEN_WIDTH, expected_y)
        for start, end in lines
    )


def test_renderer_debug_overlays_stay_in_world_viewport(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_grid = True
    renderer.show_hitboxes = True
    renderer.show_radius_overlays = True
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


def test_renderer_draws_hover_radii_only_when_r_enabled(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_radius_overlays = True
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


def test_renderer_h_toggle_does_not_draw_hover_radii(
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

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    captured_circles: list[renderer_module.Circle] = []
    original_draw_circle = renderer._draw_circle

    def capture_circle(circle: renderer_module.Circle) -> None:
        captured_circles.append(circle)
        original_draw_circle(circle)

    monkeypatch.setattr(renderer, "_draw_circle", capture_circle)

    renderer.draw(world)

    assert not any(
        circle.color == settings.DEBUG_DISCOVERY_RADIUS_COLOR
        for circle in captured_circles
    )
    assert not any(
        circle.color == settings.DEBUG_SENSE_RADIUS_COLOR
        for circle in captured_circles
    )


def test_renderer_draws_coordinate_text_only_with_g_toggle(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    renderer = renderer_module.Renderer(screen, Camera())
    world = World()
    world.ants[0].x = 100
    world.ants[0].y = 100
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    labels: list[str] = []

    def capture_debug_text(
        text: str,
        _x: int,
        _y: int,
    ) -> None:
        labels.append(text)

    monkeypatch.setattr(renderer, "_draw_debug_text", capture_debug_text)

    renderer.show_hitboxes = True
    renderer.show_radius_overlays = True
    renderer.draw(world)
    assert labels == []

    renderer.show_grid = True
    renderer.draw(world)
    assert any(label.startswith("cursor:") for label in labels)


def test_renderer_transforms_grid_labels_with_camera(
    monkeypatch,
) -> None:
    screen = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    camera = Camera()
    camera.x = 50
    camera.y = 25
    camera.zoom = 2
    renderer = renderer_module.Renderer(screen, camera)
    captured: list[tuple[str, int, int]] = []

    def capture_debug_text(text: str, x: int, y: int) -> None:
        captured.append((text, x, y))

    monkeypatch.setattr(renderer, "_draw_debug_text", capture_debug_text)

    renderer._draw_coordinate_overlay((150, 125))

    expected_x, expected_x_screen_y = (
        camera.world_to_screen(100, 0)
    )
    expected_y_screen_x, expected_y = (
        camera.world_to_screen(0, 100)
    )
    assert (
        "100",
        expected_x + 2,
        expected_x_screen_y + 2,
    ) in captured
    assert (
        "100",
        expected_y_screen_x + 2,
        expected_y + 2,
    ) in captured
