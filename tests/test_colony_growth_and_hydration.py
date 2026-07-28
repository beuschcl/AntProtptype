"""Tests for colony growth (spawning) and ant hydration."""

import random

import pytest

from ant_colony.components import (
    HydrationNeed,
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.nest import Nest
from ant_colony.ui.inspector import Inspector
from ant_colony.ui.inspector_snapshot import InspectorSnapshot
from ant_colony.world import World


def _seeded_world(seed: int = 42) -> World:
    return World(rng=random.Random(seed))


# ---------------------------------------------------------------------------
# Initial world state
# ---------------------------------------------------------------------------


def test_world_starts_with_two_ants() -> None:
    world = _seeded_world()

    assert len(world.ants) == 2


def test_world_starts_with_three_food_sources() -> None:
    world = _seeded_world()

    assert len(world.food) == 3


def test_initial_ant_ids_are_zero_and_one() -> None:
    world = _seeded_world()

    ids = sorted(ant.id for ant in world.ants)

    assert ids == [0, 1]


# ---------------------------------------------------------------------------
# Nest.consume
# ---------------------------------------------------------------------------


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

    result = nest.consume(20)

    assert result is True
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

    result = nest.consume(20)

    assert result is False
    assert nest.food_reserve == 10


def test_nest_consume_rejects_negative_cost() -> None:
    nest = Nest(x=150, y=500)

    with pytest.raises(ValueError, match="negative"):
        nest.consume(-1)


def test_nest_consume_zero_cost_succeeds() -> None:
    nest = Nest(x=150, y=500)

    result = nest.consume(0)

    assert result is True
    assert nest.food_reserve == 0


def test_nest_consume_never_goes_negative() -> None:
    nest = Nest(x=150, y=500)
    nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=5,
            ),
        )
    )

    nest.consume(20)

    assert nest.food_reserve >= 0


# ---------------------------------------------------------------------------
# Colony spawning
# ---------------------------------------------------------------------------


def _world_with_reserve(reserve: int) -> World:
    """Seeded world (2 ants, 3 food sources) with ``reserve`` nutrition in the nest."""
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


def test_world_spawns_one_ant_when_reserve_reaches_cost() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    before = len(world.ants)

    # Trigger spawning without ant movement/food collection.
    # We call update() but move food and ants away so no collection happens.
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    assert len(world.ants) == before + 1


def test_world_deducts_spawn_cost_from_nest_reserve() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    assert world.nest.food_reserve == 0


def test_world_spawns_only_one_ant_per_update_even_with_excess_reserve() -> None:
    # Give enough for two spawns
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST * 2)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0
    before = len(world.ants)

    world.update()

    assert len(world.ants) == before + 1


def test_spawned_ant_appears_at_nest_position() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    nest_x, nest_y = settings.NEST_POSITION
    new_ant = max(world.ants, key=lambda a: a.id)
    assert new_ant.x == nest_x
    assert new_ant.y == nest_y


def test_spawned_ant_has_next_sequential_id() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0
    expected_id = settings.STARTING_ANTS  # next unused ID after 0, 1

    world.update()

    ids = sorted(ant.id for ant in world.ants)
    assert expected_id in ids


def test_spawned_ant_is_fully_hydrated_at_creation() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    new_ant = max(world.ants, key=lambda a: a.id)
    assert new_ant.hydration.current == settings.ANT_MAX_HYDRATION


def test_spawned_ant_does_not_decay_in_creation_update() -> None:
    """The new ant must not receive an entity.update() call this tick."""
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    new_ant = max(world.ants, key=lambda a: a.id)
    # Hydration must still be at the maximum — no decay yet
    assert new_ant.hydration.current == settings.ANT_MAX_HYDRATION


def test_world_does_not_spawn_ant_at_max_ants() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST * 10)
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    # Fill colony to the cap by directly adding ants
    while len(world.ants) < settings.MAX_ANTS:
        ant_id = max(a.id for a in world.ants) + 1
        dummy = Ant(ant_id)
        world.add_entity(dummy)

    reserve_before = world.nest.food_reserve
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    assert len(world.ants) == settings.MAX_ANTS
    assert world.nest.food_reserve == reserve_before


# ---------------------------------------------------------------------------
# Food-source depletion cap
# ---------------------------------------------------------------------------


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


def test_food_depletion_never_exceeds_three_sources() -> None:
    world = _seeded_world()

    # Deplete all food sources one by one across multiple updates
    for _ in range(6):
        for food in world.food:
            while food.quantity > 1:
                food.collect()
        ant = world.ants[0]
        ant.x = world.food[0].x
        ant.y = world.food[0].y
        ant.speed = 0
        world.update()

        assert len(world.food) <= settings.STARTING_FOOD_SOURCES


# ---------------------------------------------------------------------------
# Hydration component (unit tests)
# ---------------------------------------------------------------------------


def test_hydration_initialises_at_maximum() -> None:
    need = HydrationNeed(maximum=100.0)

    assert need.current == 100.0
    assert need.maximum == 100.0


def test_ants_own_independent_hydration() -> None:
    ant_a = Ant(ant_id=10)
    ant_b = Ant(ant_id=11)

    ant_a.hydration.decay(50.0)

    assert ant_a.hydration.current < ant_b.hydration.current


def test_hydration_decays_exactly_once_per_ant_update() -> None:
    ant = Ant(ant_id=1)
    ant.x = settings.ANT_BOUNDARY_PADDING
    ant.y = settings.ANT_BOUNDARY_PADDING
    ant.speed = 0
    initial = ant.hydration.current

    ant.update()

    assert ant.hydration.current == pytest.approx(
        initial - settings.ANT_HYDRATION_DECAY_PER_UPDATE
    )


def test_hydration_clamps_at_zero() -> None:
    need = HydrationNeed(maximum=100.0)

    need.decay(200.0)

    assert need.current == 0.0


def test_hydration_restore_clamps_at_maximum() -> None:
    need = HydrationNeed(maximum=100.0)
    need.decay(50.0)

    need.restore(200.0)

    assert need.current == 100.0


def test_hydration_restore_partial_amount() -> None:
    need = HydrationNeed(maximum=100.0)
    need.decay(30.0)

    need.restore(10.0)

    assert need.current == pytest.approx(80.0)


# ---------------------------------------------------------------------------
# Inspector snapshot includes hydration
# ---------------------------------------------------------------------------


def test_snapshot_includes_selected_ant_hydration() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_hydration == pytest.approx(
        settings.ANT_MAX_HYDRATION
    )
    assert snapshot.selected_ant_hydration_max == pytest.approx(
        settings.ANT_MAX_HYDRATION
    )


def test_snapshot_hydration_is_none_when_no_ant_selected() -> None:
    world = _seeded_world()

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_hydration is None
    assert snapshot.selected_ant_hydration_max is None


def test_inspector_selected_ant_lines_include_hydration() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    ant.hydration.decay(0.1)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)
    lines = Inspector._selected_ant_lines(snapshot)

    hydration_lines = [
        line for line in lines if line.startswith("Hydration:")
    ]
    assert len(hydration_lines) == 1
    # Must show one decimal place
    expected = (
        f"Hydration: "
        f"{ant.hydration.current:.1f}"
        f"/{ant.hydration.maximum:.1f}"
    )
    assert hydration_lines[0] == expected


def test_inspector_hydration_format_one_decimal_place() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    # Decay a known amount so the value is predictable
    ant.hydration.decay(0.15)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)
    lines = Inspector._selected_ant_lines(snapshot)

    hydration_line = next(
        line for line in lines if line.startswith("Hydration:")
    )
    # Format: "Hydration: X.X/Y.Y"
    _, values_part = hydration_line.split(": ", 1)
    current_str, max_str = values_part.split("/")
    assert "." in current_str
    assert len(current_str.split(".")[1]) == 1
    assert "." in max_str
    assert len(max_str.split(".")[1]) == 1
