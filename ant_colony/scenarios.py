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
    route_blockers: tuple[RectangleObstacle, ...] = ()
    route_blocker_activation_tick: int | None = None
    route_blocker_activation_trip_count: int | None = None


DEFAULT_SCENARIO = Scenario(
    name=settings.DEFAULT_SCENARIO_NAME,
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
    name=settings.NAVIGATION_TEST_ARENA_NAME,
    nest_position=settings.NAVIGATION_TEST_ARENA_NEST_POSITION,
    initial_food_positions=(
        settings.NAVIGATION_TEST_ARENA_INITIAL_FOOD_POSITIONS
    ),
    obstacles=tuple(
        RectangleObstacle(
            x=x,
            y=y,
            width=width,
            height=height,
        )
        for x, y, width, height in settings.NAVIGATION_TEST_ARENA_OBSTACLES
    ),
)

ROUTE_REASSESSMENT_ARENA = Scenario(
    name=settings.ROUTE_REASSESSMENT_ARENA_NAME,
    nest_position=settings.ROUTE_REASSESSMENT_ARENA_NEST_POSITION,
    initial_food_positions=(
        settings.ROUTE_REASSESSMENT_ARENA_INITIAL_FOOD_POSITIONS
    ),
    obstacles=tuple(
        RectangleObstacle(
            x=x,
            y=y,
            width=width,
            height=height,
        )
        for x, y, width, height
        in settings.ROUTE_REASSESSMENT_ARENA_OBSTACLES
    ),
    route_blockers=tuple(
        RectangleObstacle(
            x=x,
            y=y,
            width=width,
            height=height,
        )
        for x, y, width, height
        in settings.ROUTE_REASSESSMENT_ARENA_BLOCKERS
    ),
    route_blocker_activation_tick=(
        None
    ),
    route_blocker_activation_trip_count=(
        settings.ROUTE_REASSESSMENT_ARENA_BLOCKER_ACTIVATION_TRIP_COUNT
    ),
)


_SCENARIOS = {
    DEFAULT_SCENARIO.name: DEFAULT_SCENARIO,
    NAVIGATION_TEST_ARENA.name: NAVIGATION_TEST_ARENA,
    ROUTE_REASSESSMENT_ARENA.name: ROUTE_REASSESSMENT_ARENA,
}


def get_scenario(name: str) -> Scenario:
    try:
        return _SCENARIOS[name]
    except KeyError as error:
        available = ", ".join(sorted(_SCENARIOS))
        raise ValueError(
            f"Unknown scenario '{name}'. Available scenarios: {available}."
        ) from error
