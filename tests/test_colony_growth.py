"""Tests for colony growth and food-only world setup."""

import random

import pytest

from ant_colony.components import ResourcePortion, ResourceType
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.nest import Nest
from ant_colony.world import World


def _seeded_world(seed: int = 42) -> World:
    return World(rng=random.Random(seed))


def test_world_starts_with_two_ants() -> None:
    world = _seeded_world()
    assert len(world.ants) == 2


def test_world_starts_with_three_food_sources() -> None:
    world = _seeded_world()
    assert len(world.food) == 3


def test_world_resources_are_food_only() -> None:
    world = _seeded_world()
    assert all(
        resource.resource_type is ResourceType.FOOD
        for resource in world.resources
    )


def test_world_no_longer_exposes_water_or_building_material_collections() -> None:
    world = _seeded_world()
    assert not hasattr(world, "water")
    assert not hasattr(world, "building_materials")


def test_nest_consume_deducts_exact_cost() -> None:
    nest = Nest(x=150, y=500)
    nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=30,
            ),
        )
    )
    assert nest.consume(20) is True
    assert nest.food_reserve == 10


def test_nest_consume_returns_false_when_insufficient() -> None:
    nest = Nest(x=150, y=500)
    nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=10,
            ),
        )
    )
    assert nest.consume(20) is False
    assert nest.food_reserve == 10


def test_nest_consume_rejects_negative_cost() -> None:
    nest = Nest(x=150, y=500)
    with pytest.raises(ValueError, match="negative"):
        nest.consume(-1)


def _world_with_reserve(reserve: int) -> World:
    world = _seeded_world()
    if reserve > 0:
        world.nest.deposit(
            (
                ResourcePortion(
                    source_id=1,
                    resource_type=ResourceType.FOOD,
                    value=reserve,
                ),
            )
        )
    return world


def _freeze_for_spawn_only(world: World) -> None:
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0


def test_world_spawns_one_ant_when_reserve_reaches_cost() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    before = len(world.ants)
    _freeze_for_spawn_only(world)
    world.update()
    assert len(world.ants) == before + 1


def test_world_deducts_spawn_cost_from_nest_reserve() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    _freeze_for_spawn_only(world)
    world.update()
    assert world.nest.food_reserve == 0


def test_world_spawns_only_one_ant_per_update_even_with_excess_reserve() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST * 2)
    _freeze_for_spawn_only(world)
    before = len(world.ants)
    world.update()
    assert len(world.ants) == before + 1


def test_spawned_ant_appears_at_nest_position() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    _freeze_for_spawn_only(world)
    world.update()
    nest_x, nest_y = settings.NEST_POSITION
    new_ant = max(world.ants, key=lambda a: a.id)
    assert new_ant.x == nest_x
    assert new_ant.y == nest_y


def test_world_does_not_spawn_ant_at_max_ants() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST * 10)
    _freeze_for_spawn_only(world)
    while len(world.ants) < settings.MAX_ANTS:
        ant_id = max(a.id for a in world.ants) + 1
        world.add_entity(Ant(ant_id))

    reserve_before = world.nest.food_reserve
    world.update()

    assert len(world.ants) == settings.MAX_ANTS
    assert world.nest.food_reserve == reserve_before


def test_food_depletion_replacement_keeps_count_at_three() -> None:
    world = _seeded_world()
    food = world.food[0]
    while food.quantity > 1:
        food.collect()
    ant = world.ants[0]
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    world.update()
    assert len(world.food) == settings.STARTING_FOOD_SOURCES


def _ant_state(ant: Ant) -> tuple[float, float, float, float]:
    return (ant.x, ant.y, ant.speed, ant.heading)


def test_same_seed_produces_identical_initial_ant_positions() -> None:
    world_a = World(rng=random.Random(99))
    world_b = World(rng=random.Random(99))
    states_a = sorted(_ant_state(a) for a in world_a.ants)
    states_b = sorted(_ant_state(b) for b in world_b.ants)
    assert states_a == states_b


def test_different_seeds_produce_different_initial_ant_positions() -> None:
    world_a = World(rng=random.Random(1))
    world_b = World(rng=random.Random(2))
    states_a = sorted(_ant_state(a) for a in world_a.ants)
    states_b = sorted(_ant_state(a) for a in world_b.ants)
    assert states_a != states_b
