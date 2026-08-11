import tomllib
from pathlib import Path

from ant_colony import (
    maze_pheromone_test,
    obstacle_test,
    route_reassessment_test,
)
from ant_colony.config import settings


def test_obstacle_test_launcher_uses_navigation_arena(monkeypatch) -> None:
    calls = []

    def capture_main(**kwargs) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(obstacle_test, "main", capture_main)

    obstacle_test.main_obstacle_test()

    assert calls == [
        {
            "scenario_name": settings.NAVIGATION_TEST_ARENA_NAME,
            "show_grid": True,
            "show_hitboxes": True,
            "show_radius_overlays": True,
            "window_title": f"{settings.WINDOW_TITLE} - Obstacle Test",
        }
    ]


def test_obstacle_test_console_script_is_registered() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        pyproject["project"]["scripts"]["ant-colony-obstacle-test"]
        == "ant_colony.obstacle_test:main_obstacle_test"
    )


def test_route_reassessment_launcher_uses_reassessment_arena(
    monkeypatch,
) -> None:
    calls = []

    def capture_main(**kwargs) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(route_reassessment_test, "main", capture_main)

    route_reassessment_test.main_route_reassessment_test()

    assert calls == [
        {
            "scenario_name": settings.ROUTE_REASSESSMENT_ARENA_NAME,
            "show_grid": True,
            "show_hitboxes": True,
            "show_radius_overlays": True,
            "window_title": (
                f"{settings.WINDOW_TITLE} - Route Reassessment Test"
            ),
        }
    ]


def test_route_reassessment_console_script_is_registered() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        pyproject["project"]["scripts"][
            "ant-colony-route-reassessment-test"
        ]
        == (
            "ant_colony.route_reassessment_test:"
            "main_route_reassessment_test"
        )
    )


def test_maze_pheromone_launcher_uses_maze_arena(
    monkeypatch,
) -> None:
    calls = []

    def capture_main(**kwargs) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(maze_pheromone_test, "main", capture_main)

    maze_pheromone_test.main_maze_pheromone_test()

    assert calls == [
        {
            "scenario_name": settings.MAZE_PHEROMONE_ARENA_NAME,
            "show_grid": True,
            "show_hitboxes": True,
            "show_radius_overlays": True,
            "window_title": (
                f"{settings.WINDOW_TITLE} - Maze Pheromone Test"
            ),
        }
    ]


def test_maze_pheromone_console_script_is_registered() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        pyproject["project"]["scripts"][
            "ant-colony-maze-pheromone-test"
        ]
        == (
            "ant_colony.maze_pheromone_test:"
            "main_maze_pheromone_test"
        )
    )
