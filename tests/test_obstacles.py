import random

import pytest

from ant_colony.components import AntState, ResourcePortion, ResourceType
from ant_colony.config import settings
from ant_colony.entities.pheromone import PheromoneType
from ant_colony.geometry import RectangleObstacle
from ant_colony.scenarios import (
    NAVIGATION_TEST_ARENA,
    ROUTE_REASSESSMENT_ARENA,
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

    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.x < 500


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


def test_seeking_ant_escapes_obstacle_corner_contact() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 530
    ant.y = 330
    ant.speed = 5
    food.x = 780
    food.y = 350
    ant.select_food_target(food)

    world._update_ant_movement(ant)

    assert ant.x > 530
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


def test_returning_ant_escapes_obstacle_corner_contact() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 530
    ant.y = 330
    ant.speed = 5
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=1,
        )
    )
    ant.select_nest_target(world.nest)

    world._update_ant_movement(ant)

    assert (ant.x, ant.y) != (530, 330)
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.nest_target is world.nest


def test_seeking_ant_escapes_obstacle_ceiling_corner_contact() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 518
    ant.y = settings.ANT_BOUNDARY_PADDING
    ant.speed = 5
    food.x = 780
    food.y = 350
    ant.select_food_target(food)

    for _ in range(200):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            food,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

    assert ant.intersects_entity(
        food,
        padding=settings.ANT_INTERACTION_RADIUS,
    )
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


def test_returning_ant_escapes_obstacle_ceiling_corner_contact() -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 518
    ant.y = settings.ANT_BOUNDARY_PADDING
    ant.speed = 5
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=1,
        )
    )
    ant.select_nest_target(world.nest)

    for _ in range(200):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            world.nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

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


def _world_boundary_obstacle_contact_points() -> tuple[tuple[float, float], ...]:
    world = World(scenario="navigation_test_arena")
    points: list[tuple[float, float]] = []
    padding = settings.ANT_BOUNDARY_PADDING

    for obstacle in world.obstacles:
        contact_x_values = (
            obstacle.x - padding,
            obstacle.x + obstacle.width / 2,
            obstacle.x + obstacle.width + padding,
        )
        if obstacle.y <= 0:
            points.extend((x, padding) for x in contact_x_values)
        if obstacle.y + obstacle.height >= settings.WORLD_HEIGHT:
            points.extend(
                (x, settings.WORLD_HEIGHT - padding)
                for x in contact_x_values
            )

    return tuple(points)


def _world_boundary_obstacle_nearby_points() -> tuple[tuple[float, float], ...]:
    world = World(scenario="navigation_test_arena")
    points: list[tuple[float, float]] = []
    padding = settings.ANT_BOUNDARY_PADDING
    exterior_offset = padding + (settings.ANT_RADIUS * 2)

    for obstacle in world.obstacles:
        nearby_x_values = (
            obstacle.x - exterior_offset,
            obstacle.x + obstacle.width + exterior_offset,
        )
        if obstacle.y <= 0:
            points.extend((x, padding) for x in nearby_x_values)
        if obstacle.y + obstacle.height >= settings.WORLD_HEIGHT:
            points.extend(
                (x, settings.WORLD_HEIGHT - padding)
                for x in nearby_x_values
            )

    return tuple(points)


@pytest.mark.parametrize("point", _world_boundary_obstacle_contact_points())
@pytest.mark.parametrize("wall_follow_side", (-1, 1))
def test_seeking_ant_recovers_from_world_boundary_obstacle_contact(
    point: tuple[float, float],
    wall_follow_side: int,
) -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x, ant.y = point
    ant.speed = 5
    food.x = 780
    food.y = 350
    ant.select_food_target(food)
    world._wall_follow_sides[ant.id] = wall_follow_side

    for _ in range(300):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            food,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

    assert ant.intersects_entity(
        food,
        padding=settings.ANT_INTERACTION_RADIUS,
    )
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


@pytest.mark.parametrize("point", _world_boundary_obstacle_contact_points())
@pytest.mark.parametrize("wall_follow_side", (-1, 1))
def test_returning_ant_recovers_from_world_boundary_obstacle_contact(
    point: tuple[float, float],
    wall_follow_side: int,
) -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x, ant.y = point
    ant.speed = 5
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=1,
        )
    )
    ant.select_nest_target(world.nest)
    world._wall_follow_sides[ant.id] = wall_follow_side

    for _ in range(300):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            world.nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

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


@pytest.mark.parametrize("point", _world_boundary_obstacle_nearby_points())
@pytest.mark.parametrize("wall_follow_side", (-1, 1))
def test_seeking_ant_recovers_near_world_boundary_obstacle(
    point: tuple[float, float],
    wall_follow_side: int,
) -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x, ant.y = point
    ant.speed = 5
    food.x = 780
    food.y = 350
    ant.select_food_target(food)
    world._wall_follow_sides[ant.id] = wall_follow_side

    for _ in range(300):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            food,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

    assert ant.intersects_entity(
        food,
        padding=settings.ANT_INTERACTION_RADIUS,
    )
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
    assert ant.food_target is food


@pytest.mark.parametrize("point", _world_boundary_obstacle_nearby_points())
@pytest.mark.parametrize("wall_follow_side", (-1, 1))
def test_returning_ant_recovers_near_world_boundary_obstacle(
    point: tuple[float, float],
    wall_follow_side: int,
) -> None:
    world = World(scenario="navigation_test_arena")
    ant = world.ants[0]
    food = world.food[0]
    ant.x, ant.y = point
    ant.speed = 5
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=1,
        )
    )
    ant.select_nest_target(world.nest)
    world._wall_follow_sides[ant.id] = wall_follow_side

    for _ in range(300):
        world._update_ant_movement(ant)
        if ant.intersects_entity(
            world.nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

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


def test_route_reassessment_arena_starts_with_short_route_open() -> None:
    world = World(scenario=ROUTE_REASSESSMENT_ARENA)

    assert world.scenario_name == settings.ROUTE_REASSESSMENT_ARENA_NAME
    assert not world.route_blockers_active
    assert world.route_blockers == ROUTE_REASSESSMENT_ARENA.route_blockers
    assert len(world.obstacles) == len(
        ROUTE_REASSESSMENT_ARENA.obstacles
    )

    assert not world._position_is_blocked(500, 320)
    assert not world._position_is_blocked(500, 520)


def _begin_food_return_through_short_route(world: World) -> None:
    ant = world.ants[0]
    food = world.food[0]
    ant.x = food.x
    ant.y = food.y
    ant.inventory.clear()
    ant.state = AntState.WANDERING
    ant.select_food_target(food)

    world._collect_food_for(ant)


def test_route_reassessment_arena_closes_short_route_on_third_return() -> None:
    world = World(scenario=ROUTE_REASSESSMENT_ARENA)

    for _ in range(
        settings.ROUTE_REASSESSMENT_ARENA_BLOCKER_ACTIVATION_TRIP_COUNT - 1
    ):
        _begin_food_return_through_short_route(world)

    assert not world.route_blockers_active
    assert world.route_blocker_trip_count == 2

    _begin_food_return_through_short_route(world)

    assert world.route_blockers_active
    assert world.route_blocker_trip_count == 3
    assert len(world.obstacles) == (
        len(ROUTE_REASSESSMENT_ARENA.obstacles)
        + len(ROUTE_REASSESSMENT_ARENA.route_blockers)
    )
    assert world._position_is_blocked(500, 320)
    assert not world._position_is_blocked(500, 520)


def test_ant_reaches_food_through_alternate_route_after_short_route_closes() -> None:
    world = World(scenario=ROUTE_REASSESSMENT_ARENA)
    world._active_route_blockers = world.route_blockers
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 460
    ant.y = 320
    ant.speed = 5
    ant.select_food_target(food)

    lowest_y = ant.y
    for _ in range(450):
        world._update_ant_movement(ant)
        lowest_y = max(lowest_y, ant.y)
        if ant.intersects_entity(
            food,
            padding=settings.ANT_INTERACTION_RADIUS,
        ):
            break

    assert ant.intersects_entity(
        food,
        padding=settings.ANT_INTERACTION_RADIUS,
    )
    assert lowest_y > 460
    assert not world._position_is_blocked(
        ant.x,
        ant.y,
        radius=ant.hitbox_radius,
    )
