from types import SimpleNamespace

import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui import renderer as renderer_module
from ant_colony.ui.window_layout import WindowLayout
from ant_colony.world import World


def test_renderer_draws_world_bounds_and_divider() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())
    world = SimpleNamespace(
        entities=(),
        selected_ant=None,
        entity_under_position=lambda _: None,
    )
    layout = WindowLayout.calculate(
        screen.get_size(),
        settings.INSPECTOR_WIDTH,
    )

    renderer.draw(world, layout)

    assert (
        screen.get_at(layout.world_viewport.topleft)[:3]
        == settings.SCOPE_BOUNDARY_COLOR
    )
    assert (
        screen.get_at(layout.divider_rect.center)[:3]
        == settings.INSPECTOR_DIVIDER_COLOR
    )


def test_renderer_draws_ants_with_primitives(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())
    world = World()
    ant = world.ants[0]
    ant.x = 100
    ant.y = 100

    drawn_shapes = []

    def capture_shape(shape: renderer_module.Shape) -> None:
        drawn_shapes.append(shape)

    monkeypatch.setattr(renderer, "_draw_shape", capture_shape)

    renderer._draw_entity(ant)

    assert drawn_shapes


def test_renderer_toggles_grid_hitboxes_and_radii_independently() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())

    renderer.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_g))
    renderer.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    renderer.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))

    assert renderer.show_grid
    assert renderer.show_hitboxes
    assert renderer.show_radius_overlays

    renderer.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))

    assert renderer.show_grid
    assert not renderer.show_hitboxes
    assert renderer.show_radius_overlays


def test_renderer_draws_camera_transformed_grid_lines(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    camera = Camera()
    renderer = renderer_module.Renderer(screen, camera)
    renderer.show_grid = True
    world = World()
    lines: list[tuple[tuple[int, int], tuple[int, int]]] = []

    def capture_line(
        _surface: pygame.Surface,
        _color: tuple[int, int, int],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        lines.append((start, end))

    monkeypatch.setattr(pygame.draw, "line", capture_line)

    layout = WindowLayout.calculate((1600, 900), 300)
    renderer.draw(world, layout)

    expected_x, _ = camera.world_to_screen(100, 0)
    _, expected_y = camera.world_to_screen(0, 100)
    assert any(start[0] == expected_x and end[0] == expected_x for start, end in lines)
    assert any(start[1] == expected_y and end[1] == expected_y for start, end in lines)


def test_renderer_debug_overlays_stay_in_world_viewport(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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


def test_renderer_does_not_mutate_world_state(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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


def test_renderer_draws_hover_radii_only_when_r_enabled(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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


def test_renderer_h_toggle_does_not_draw_hover_radii(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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


def test_renderer_draws_coordinate_text_only_with_g_toggle(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())
    world = World()
    world.ants[0].x = 100
    world.ants[0].y = 100
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    labels: list[str] = []

    def capture_debug_text(text: str, _x: int, _y: int) -> None:
        labels.append(text)

    monkeypatch.setattr(renderer, "_draw_debug_text", capture_debug_text)
    monkeypatch.setattr(pygame.mouse, "get_focused", lambda: True)

    renderer.show_hitboxes = True
    renderer.show_radius_overlays = True
    renderer.draw(world)
    assert labels == []

    renderer.show_grid = True
    renderer.draw(world)
    assert any(label.startswith("cursor:") for label in labels)


def test_renderer_hides_cursor_coordinates_outside_world_viewport(monkeypatch) -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_grid = True
    world = World()
    labels: list[str] = []

    def capture_debug_text(text: str, _x: int, _y: int) -> None:
        labels.append(text)

    monkeypatch.setattr(renderer, "_draw_debug_text", capture_debug_text)

    monkeypatch.setattr(
        pygame.mouse,
        "get_pos",
        lambda: (settings.WORLD_WIDTH + 20, 100),
    )
    monkeypatch.setattr(pygame.mouse, "get_focused", lambda: True)
    renderer.draw(world)
    assert not any(label.startswith("cursor:") for label in labels)

    labels.clear()
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (100, 100))
    monkeypatch.setattr(pygame.mouse, "get_focused", lambda: False)
    renderer.draw(world)
    assert not any(label.startswith("cursor:") for label in labels)


def test_renderer_obstacle_debug_bounds_stay_in_world_viewport() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    renderer = renderer_module.Renderer(screen, Camera())
    renderer.show_hitboxes = True
    world = World(scenario="navigation_test_arena")

    renderer.draw(world)

    assert (
        screen.get_at((settings.WORLD_WIDTH + 20, 20))[:3]
        == settings.BACKGROUND_COLOR
    )
