import random

import pytest

from ant_colony.components import ResourcePortion, ResourceType
from ant_colony.config import settings
from ant_colony.entities.pheromone import PheromoneType
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


def test_blocked_ant_tries_clear_alternate_heading() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 460
    ant.y = 370
    ant.speed = 10
    food.x = 780
    food.y = 370
    ant.select_food_target(food)

    world._update_ant_movement(ant)

    assert ant.x > 460
    assert ant.y != 370
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


def test_blocked_targeted_ant_enters_wall_follow_recovery() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 460
    ant.y = 370
    ant.speed = 10
    food.x = 780
    food.y = 370
    ant.select_food_target(food)

    world._update_ant_movement(ant)

    assert ant.id in world._wall_follow_sides
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


def test_first_return_trip_reaches_nest_without_pheromone_help() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 780
    ant.y = 370
    ant.speed = 5
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=1,
        )
    )
    ant.select_nest_target(world.nest)

    for _ in range(250):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            world.nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

    assert all(
        pheromone.pheromone_type != PheromoneType.FOOD
        for pheromone in world.pheromones
    )
    assert ant.intersects_entity(
        world.nest,
        padding=settings.ANT_INTERACTION_RADIUS,
    )
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.nest_target is world.nest


def test_repeated_blocked_ant_drops_avoid_pheromone() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    ant.x = 475
    ant.y = 370
    ant.speed = 10

    world._record_blocked_heading(ant, 0)
    blocked_count = world._record_blocked_heading(ant, 0)
    if blocked_count >= settings.ANT_AVOID_PHEROMONE_REPEAT_COUNT:
        world._deposit_avoid_pheromone_for(ant)

    assert world.pheromones[-1].pheromone_type == PheromoneType.AVOID
    assert world.pheromones[-1].source_food_id is None


def test_repeated_blocked_ant_prefers_backing_up_to_wall_sliding() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 460
    ant.y = 370
    ant.speed = 10
    food.x = 780
    food.y = 370
    ant.select_food_target(food)

    world._move_ant_around_obstacle(
        ant,
        blocked_count=settings.ANT_AVOID_PHEROMONE_REPEAT_COUNT,
    )

    assert ant.x < 460
    assert ant.y == 370
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )


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
