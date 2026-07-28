"""Tests for thirst / water-seeking behavior."""

from __future__ import annotations

import random

import pytest

from ant_colony.components import (
    AntState,
    FoodTargetSource,
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.food import Food
from ant_colony.entities.water import Water
from ant_colony.ui.inspector_snapshot import InspectorSnapshot
from ant_colony.world import World

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seeded_world(seed: int = 42) -> World:
    return World(rng=random.Random(seed))


def _ant_at(x: float, y: float, speed: float = 0.0) -> Ant:
    ant = Ant(ant_id=99, rng=random.Random(0))
    ant.x = x
    ant.y = y
    ant.speed = speed
    return ant


def _water_at(x: float, y: float) -> Water:
    return Water(
        water_id=10,
        x=x,
        y=y,
        hydration=4,
        quantity=15,
    )


def _food_at(x: float, y: float) -> Food:
    return Food(
        food_id=10,
        x=x,
        y=y,
        nutrition=5,
        quantity=10,
    )


# ---------------------------------------------------------------------------
# Thirst threshold
# ---------------------------------------------------------------------------


def test_ant_is_not_thirsty_above_threshold() -> None:
    ant = Ant(ant_id=1)
    # hydration starts at maximum (100); must be strictly above 90
    ant.hydration.restore(0)  # keeps at maximum
    assert ant.hydration.current == settings.ANT_MAX_HYDRATION
    assert not ant.is_thirsty


def test_ant_is_thirsty_at_threshold() -> None:
    ant = Ant(ant_id=1)
    # Drain to exactly the threshold
    decay = ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD
    ant.hydration.decay(decay)

    assert ant.hydration.current == pytest.approx(settings.ANT_THIRST_THRESHOLD)
    assert ant.is_thirsty


def test_ant_is_thirsty_below_threshold() -> None:
    ant = Ant(ant_id=1)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD + 1.0)

    assert ant.hydration.current < settings.ANT_THIRST_THRESHOLD
    assert ant.is_thirsty


def test_ant_is_not_thirsty_just_above_threshold() -> None:
    ant = Ant(ant_id=1)
    # Leave just a tiny bit above the threshold
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD - 0.01)

    assert ant.hydration.current > settings.ANT_THIRST_THRESHOLD
    assert not ant.is_thirsty


# ---------------------------------------------------------------------------
# Water target selection on Ant
# ---------------------------------------------------------------------------


def test_select_water_target_sets_state_to_seeking_water() -> None:
    ant = _ant_at(100, 100)
    water = _water_at(300, 300)

    ant.select_water_target(water)

    assert ant.water_target is water
    assert ant.state == AntState.SEEKING_WATER


def test_select_water_target_clears_food_target() -> None:
    ant = _ant_at(100, 100)
    food = _food_at(200, 200)
    water = _water_at(300, 300)
    ant.select_food_target(food)

    ant.select_water_target(water)

    assert ant.food_target is None
    assert ant.water_target is water


def test_clear_water_target_sets_state_to_wandering() -> None:
    ant = _ant_at(100, 100)
    water = _water_at(300, 300)
    ant.select_water_target(water)

    ant.clear_water_target()

    assert ant.water_target is None
    assert ant.state == AntState.WANDERING


# ---------------------------------------------------------------------------
# can_drink / drink_from
# ---------------------------------------------------------------------------


def test_ant_can_drink_when_at_spring() -> None:
    water = _water_at(300, 300)
    ant = _ant_at(300, 300)

    assert ant.can_drink(water)


def test_ant_cannot_drink_when_far_from_spring() -> None:
    water = _water_at(300, 300)
    ant = _ant_at(0, 0)

    assert not ant.can_drink(water)


def test_drink_from_restores_hydration_to_maximum() -> None:
    water = _water_at(300, 300)
    ant = _ant_at(300, 300)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    assert ant.hydration.current == pytest.approx(settings.ANT_THIRST_THRESHOLD)
    ant.drink_from(water)

    assert ant.hydration.current == pytest.approx(ant.hydration.maximum)


def test_drink_from_fully_restores_partial_hydration() -> None:
    water = _water_at(200, 200)
    ant = _ant_at(200, 200)
    ant.hydration.decay(50.0)

    ant.drink_from(water)

    assert ant.hydration.current == pytest.approx(ant.hydration.maximum)


def test_drink_from_clears_water_target() -> None:
    water = _water_at(200, 200)
    ant = _ant_at(200, 200)
    ant.select_water_target(water)

    ant.drink_from(water)

    assert ant.water_target is None


def test_drink_from_sets_state_to_wandering() -> None:
    water = _water_at(200, 200)
    ant = _ant_at(200, 200)
    ant.select_water_target(water)

    ant.drink_from(water)

    assert ant.state == AntState.WANDERING


def test_drink_from_clears_on_excursion_flag() -> None:
    water = _water_at(200, 200)
    ant = _ant_at(200, 200)
    ant.energy.restore(ant.energy.maximum)
    ant.depart()  # sets on_excursion = True
    ant.select_water_target(water)

    ant.drink_from(water)

    assert not ant.on_excursion


def test_drink_from_returns_false_when_far() -> None:
    water = _water_at(500, 500)
    ant = _ant_at(0, 0)
    ant.select_water_target(water)

    result = ant.drink_from(water)

    assert result is False
    assert ant.state == AntState.SEEKING_WATER


def test_water_quantity_unchanged_after_drinking() -> None:
    """Water is unlimited — quantity must not decrease when an ant drinks."""
    water = _water_at(200, 200)
    ant = _ant_at(200, 200)
    initial_quantity = water.quantity

    ant.drink_from(water)

    assert water.quantity == initial_quantity


# ---------------------------------------------------------------------------
# Ant.update() with SEEKING_WATER state
# ---------------------------------------------------------------------------


def test_ant_update_moves_toward_water_when_seeking() -> None:
    water = _water_at(300, 300)
    ant = _ant_at(100, 100, speed=2.0)
    ant.select_water_target(water)
    initial_x = ant.x

    ant.update()

    assert ant.x > initial_x


def test_ant_at_zero_hydration_does_not_wander() -> None:
    """An ant at 0 hydration in WANDERING state stays put (waits)."""
    ant = _ant_at(200, 200, speed=2.0)
    ant.hydration.decay(ant.hydration.maximum)  # drain to 0
    assert ant.hydration.current == 0.0
    initial_x = ant.x
    initial_y = ant.y

    ant.update()  # WANDERING + hydration 0 → no wander

    assert ant.x == initial_x
    assert ant.y == initial_y


# ---------------------------------------------------------------------------
# World._assign_water_target
# ---------------------------------------------------------------------------


def test_world_assigns_water_target_to_thirsty_wandering_ant() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    # Make the ant thirsty
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)
    # Freeze other ants so they don't interfere
    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world._assign_water_target(ant, ())

    assert ant.water_target is not None
    assert ant.state == AntState.SEEKING_WATER


def test_world_does_not_assign_water_to_hydrated_ant() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    # Ant starts fully hydrated
    assert not ant.is_thirsty

    world._assign_water_target(ant, ())

    assert ant.water_target is None
    assert ant.state == AntState.WANDERING


def test_world_does_not_assign_water_to_carrying_ant() -> None:
    """Food delivery takes priority: CARRYING_FOOD ants are not redirected."""
    world = _seeded_world()
    ant = world.ants[0]
    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(world.nest)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    world._assign_water_target(ant, ())

    assert ant.water_target is None
    assert ant.state == AntState.CARRYING_FOOD


def test_world_does_not_replace_existing_water_target() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    world._assign_water_target(ant, ())
    first_target = ant.water_target

    world._assign_water_target(ant, ())

    assert ant.water_target is first_target


def test_world_redirects_seeking_food_ant_to_water_when_thirsty() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    food = world.food[0]
    ant.select_food_target(food)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    world._assign_water_target(ant, ())

    assert ant.water_target is not None
    assert ant.food_target is None
    assert ant.state == AntState.SEEKING_WATER


# ---------------------------------------------------------------------------
# Deterministic water targeting
# ---------------------------------------------------------------------------


def test_water_targeting_is_deterministic() -> None:
    """Same world with same RNG must always pick the same water source."""
    world_a = World(rng=random.Random(99))
    world_b = World(rng=random.Random(99))

    ant_a = world_a.ants[0]
    ant_b = world_b.ants[0]

    ant_a.hydration.decay(ant_a.hydration.maximum - settings.ANT_THIRST_THRESHOLD)
    ant_b.hydration.decay(ant_b.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    world_a._assign_water_target(ant_a, ())
    world_b._assign_water_target(ant_b, ())

    assert ant_a.water_target is not None
    assert ant_b.water_target is not None
    assert ant_a.water_target.id == ant_b.water_target.id


def test_water_target_selected_by_closest_then_id() -> None:
    """When multiple water sources exist, the closest (then lowest id) wins."""
    world = _seeded_world()
    # Place two extra water sources; one much closer to ant
    near_water = Water(water_id=20, x=200, y=200, hydration=4, quantity=5)
    far_water = Water(water_id=21, x=800, y=600, hydration=4, quantity=5)
    world.add_entity(near_water)
    world.add_entity(far_water)

    ant = world.ants[0]
    ant.x = 200
    ant.y = 200
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    world._assign_water_target(ant, ())

    assert ant.water_target is near_water


# ---------------------------------------------------------------------------
# World._drink_water_for
# ---------------------------------------------------------------------------


def test_world_processes_drinking_at_spring() -> None:
    world = _seeded_world()
    spring = world.water[0]
    ant = world.ants[0]

    ant.x = spring.x
    ant.y = spring.y
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)
    ant.select_water_target(spring)

    result = world._drink_water_for(ant)

    assert result is True
    assert ant.hydration.current == pytest.approx(ant.hydration.maximum)
    assert ant.state == AntState.WANDERING


def test_world_drink_returns_false_when_no_water_target() -> None:
    world = _seeded_world()
    ant = world.ants[0]

    result = world._drink_water_for(ant)

    assert result is False


# ---------------------------------------------------------------------------
# Full world.update() integration
# ---------------------------------------------------------------------------


def test_thirsty_ant_assigned_water_target_during_update() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    # Make ant very thirsty so it triggers immediately
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)
    # Place ant far from food so no food target is assigned first
    ant.x = 0
    ant.y = 0
    ant.speed = 0
    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world.update()

    assert ant.water_target is not None
    assert ant.state == AntState.SEEKING_WATER


def test_ant_drinks_and_resumes_normal_behavior_via_world() -> None:
    """Full loop: thirsty ant → water target → reaches spring → drinks → WANDERING."""
    world = _seeded_world()
    spring = world.water[0]
    ant = world.ants[0]

    # Place ant at the spring and make it thirsty
    ant.x = spring.x
    ant.y = spring.y
    ant.speed = 0
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    # Freeze other ants to avoid interference
    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world.update()

    # The ant should have drunk and be back to full hydration
    assert ant.hydration.current == pytest.approx(ant.hydration.maximum)
    assert ant.state == AntState.WANDERING
    assert ant.water_target is None


def test_food_delivery_takes_priority_over_thirst_in_world() -> None:
    """A carrying ant must deliver food before seeking water.

    While the ant is in CARRYING_FOOD state (not yet at the nest), a water
    target must NOT be assigned even when the ant is thirsty.
    """
    world = _seeded_world()
    ant = world.ants[0]
    nest = world.nest

    # Place ant far from the nest so it cannot deposit this tick
    ant.x = settings.WORLD_WIDTH * 0.9
    ant.y = settings.WORLD_HEIGHT * 0.9
    ant.speed = 0  # Freeze so it stays far away

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(nest)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    # Freeze other ants so they don't interfere
    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world.update()

    # Water target must NOT be assigned while the ant is carrying food
    assert ant.water_target is None
    assert ant.state == AntState.CARRYING_FOOD


def test_ant_seeks_water_after_delivering_food() -> None:
    """After depositing food the ant should immediately seek water if still thirsty."""
    world = _seeded_world()
    ant = world.ants[0]
    nest = world.nest

    # Place ant at the nest with food and make thirsty
    ant.x = nest.x
    ant.y = nest.y
    ant.speed = 0
    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(nest)
    ant.hydration.decay(ant.hydration.maximum - settings.ANT_THIRST_THRESHOLD)

    # Freeze other ants
    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world.update()

    # Food should be deposited
    assert ant.inventory.is_empty
    # Ant should now target water
    assert ant.water_target is not None
    assert ant.state == AntState.SEEKING_WATER


def test_ant_at_zero_hydration_stays_put_when_no_water() -> None:
    """An ant at exactly 0 hydration with WANDERING state stays still (waits)."""
    world = _seeded_world()
    # Remove all water from the world
    for w in world.water:
        world.remove_entity(w)

    ant = world.ants[0]
    ant.x = 200
    ant.y = 200
    ant.speed = 2.0
    ant.hydration.decay(ant.hydration.maximum)  # drain to 0
    assert ant.hydration.current == 0.0

    # Freeze other ants
    for other in world.ants[1:]:
        other.speed = 0

    # Put ant in wandering state (no targets)
    assert ant.state == AntState.WANDERING
    initial_x = ant.x
    initial_y = ant.y

    world.update()

    # Hydration stays at 0 (clamped); ant does not move
    assert ant.hydration.current == 0.0
    assert ant.x == initial_x
    assert ant.y == initial_y


# ---------------------------------------------------------------------------
# Inspector snapshot: water target text
# ---------------------------------------------------------------------------


def test_snapshot_shows_water_thirst_target() -> None:
    world = _seeded_world()
    spring = world.water[0]
    ant = world.ants[0]

    ant.select_water_target(spring)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == "Water (thirst)"


def test_snapshot_water_target_takes_precedence_over_food() -> None:
    """If both water and food targets were somehow set, water shows in inspector."""
    world = _seeded_world()
    spring = world.water[0]
    food = world.food[0]
    ant = world.ants[0]

    # Manually set food target then override with water (as per normal flow)
    ant.select_water_target(spring)
    # Directly set food target without clearing water (edge-case guard)
    ant._food_target = food  # type: ignore[attr-defined]
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == "Water (thirst)"


# ---------------------------------------------------------------------------
# Regression: food / pheromone / memory / energy unaffected
# ---------------------------------------------------------------------------


def test_hydrated_ant_still_targets_food_normally() -> None:
    """A fully hydrated wandering ant should still be assigned food targets."""
    world = _seeded_world()
    ant = world.ants[0]
    food = world.food[0]

    # Place ant at food with enough hydration
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    assert not ant.is_thirsty

    for other in world.ants[1:]:
        other.speed = 0
        other.x = 0
        other.y = 0

    world.update()

    # Ant should collect food and NOT seek water
    assert ant.inventory.count() == 1
    assert ant.water_target is None
    assert ant.state == AntState.CARRYING_FOOD


def test_food_delivery_loop_unaffected_when_hydrated() -> None:
    """Full food delivery loop works normally when hydration is above threshold."""
    world = _seeded_world()
    ant = world.ants[0]
    food = world.food[0]
    nest = world.nest

    food.x = 200
    food.y = 200
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    for other in world.ants[1:]:
        other.x = settings.WORLD_WIDTH
        other.y = settings.WORLD_HEIGHT
        other.speed = 0
    for other_food in world.food[1:]:
        other_food.x = settings.WORLD_WIDTH
        other_food.y = settings.WORLD_HEIGHT

    world.update()

    assert ant.inventory.count() == 1
    assert ant.state == AntState.CARRYING_FOOD

    ant.x = nest.x
    ant.y = nest.y

    world.update()

    assert ant.inventory.is_empty
    # Not thirsty → should seek remembered food, not water
    assert ant.is_thirsty is False
    assert ant.food_target is food
    assert ant.water_target is None
    assert ant.state == AntState.SEEKING_FOOD


def test_post_deposit_food_target_uses_memory_when_hydrated() -> None:
    """After delivering food a well-hydrated ant returns to remembered food."""
    world = _seeded_world()
    ant = world.ants[0]
    food = world.food[0]
    nest = world.nest

    food.x = 200
    food.y = 200
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    for other in world.ants[1:]:
        other.x = settings.WORLD_WIDTH
        other.y = settings.WORLD_HEIGHT
        other.speed = 0
    for other_food in world.food[1:]:
        other_food.x = settings.WORLD_WIDTH
        other_food.y = settings.WORLD_HEIGHT

    world.update()  # collect food

    ant.x = nest.x
    ant.y = nest.y

    world.update()  # deposit

    assert ant.food_target is food
    assert ant.food_target_source == FoodTargetSource.MEMORY
    assert ant.water_target is None
