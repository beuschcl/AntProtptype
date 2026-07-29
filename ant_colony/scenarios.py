from __future__ import annotations

from dataclasses import dataclass

from ant_colony.config import settings
from ant_colony.geometry import RectangleObstacle


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    nest_position: tuple[float, float]
    initial_food_positions: tuple[
        tuple[float, float], ...
    ]
    obstacles: tuple[RectangleObstacle, ...] = ()


DEFAULT_SCENARIO = Scenario(
    name="default_centered_colony",
    nest_position=settings.NEST_POSITION,
    initial_food_positions=tuple(
        (
            settings.NEST_POSITION[0] + offset_x,
            settings.NEST_POSITION[1] + offset_y,
        )
        for offset_x, offset_y in settings.INITIAL_FOOD_SOURCE_OFFSETS
    ),
)

NAVIGATION_TEST_ARENA = Scenario(
    name="navigation_test_arena",
    nest_position=(220, settings.WORLD_HEIGHT / 2),
    initial_food_positions=(
        (780, settings.WORLD_HEIGHT / 2),
        (820, settings.WORLD_HEIGHT / 2 - 30),
        (820, settings.WORLD_HEIGHT / 2 + 30),
    ),
    obstacles=(
        RectangleObstacle(x=480, y=0, width=40, height=300),
        RectangleObstacle(x=480, y=340, width=40, height=120),
        RectangleObstacle(
            x=480,
            y=580,
            width=40,
            height=settings.WORLD_HEIGHT - 580,
        ),
    ),
)


_SCENARIOS = {
    DEFAULT_SCENARIO.name: DEFAULT_SCENARIO,
    NAVIGATION_TEST_ARENA.name: NAVIGATION_TEST_ARENA,
}


def get_scenario(name: str) -> Scenario:
    try:
        return _SCENARIOS[name]
    except KeyError as error:
        available = ", ".join(sorted(_SCENARIOS))
        raise ValueError(
            f"Unknown scenario '{name}'. Available scenarios: {available}."
        ) from error
