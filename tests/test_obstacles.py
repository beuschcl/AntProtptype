import random

import pytest

from ant_colony.config import settings
from ant_colony.geometry import RectangleObstacle
from ant_colony.scenarios import (
    NAVIGATION_TEST_ARENA,
    Scenario,
)
from ant_colony.world import World


def test_rectangle_obstacle_intersection_is_deterministic() -> None:
    obstacle = RectangleObstacle(
        x=100,
        y=100,
        width=60,
        height=30,
    )

    assert obstacle.contains_point(100, 100)
    assert obstacle.contains_point(160, 130)
    assert not obstacle.contains_point(161, 131)
    assert obstacle.intersects_circle(130, 115, 5)
    assert not obstacle.intersects_circle(10, 10, 2)
    assert obstacle.intersects_segment((0, 115), (200, 115))
    assert not obstacle.intersects_segment((0, 10), (20, 10))


def test_default_scenario_has_no_obstacles_and_updates() -> None:
    world = World(rng=random.Random(7))

    assert world.scenario_name == "default_centered_colony"
    assert world.obstacles == ()

    world.update()
    assert len(world.ants) == settings.STARTING_ANTS


def test_ant_movement_does_not_cross_obstacle() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    ant.x = 475
    ant.y = 370
    ant.speed = 10
    ant.heading = 0

    world._update_ant_movement(ant)

    assert ant.x == 475
    assert ant.y == 370


def test_spawn_rejects_blocked_nest_position() -> None:
    scenario = Scenario(
        name="blocked_nest",
        nest_position=(100, 100),
        initial_food_positions=((200, 200),),
        obstacles=(
            RectangleObstacle(
                x=80,
                y=80,
                width=60,
                height=60,
            ),
        ),
    )

    with pytest.raises(ValueError, match="blocked position"):
        World(scenario=scenario)


def test_initial_food_blocked_position_is_rejected() -> None:
    scenario = Scenario(
        name="blocked_food",
        nest_position=(80, 80),
        initial_food_positions=((120, 120),),
        obstacles=(
            RectangleObstacle(
                x=100,
                y=100,
                width=100,
                height=100,
            ),
        ),
    )
    world = World(rng=random.Random(5), scenario=scenario)

    assert len(world.food) == settings.STARTING_FOOD_SOURCES
    assert all(
        not world._position_is_blocked(
            food.x,
            food.y,
            radius=settings.FOOD_RADIUS,
        )
        for food in world.food
    )


def test_navigation_test_arena_layout_matches_expected_corridors() -> None:
    world = World(scenario=NAVIGATION_TEST_ARENA)

    assert world.nest.x < settings.WORLD_WIDTH / 2
    assert all(food.x > settings.WORLD_WIDTH / 2 for food in world.food)
    assert len(world.obstacles) == 3

    assert world._position_is_blocked(500, 370)
    assert not world._position_is_blocked(500, 320)
    assert not world._position_is_blocked(500, 520)
