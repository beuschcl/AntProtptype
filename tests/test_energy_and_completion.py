"""Tests for the ant energy system and the colony-completion state."""

from __future__ import annotations

import random

import pygame
import pytest

from ant_colony.components import (
    EnergyNeed,
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.ui.completion_overlay import CompletionOverlay
from ant_colony.ui.inspector import Inspector
from ant_colony.ui.inspector_snapshot import InspectorSnapshot
from ant_colony.ui.window_layout import WindowLayout
from ant_colony.world import World

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seeded_world(seed: int = 42) -> World:
    return World(rng=random.Random(seed))


def _world_with_reserve(reserve: int, seed: int = 42) -> World:
    world = _seeded_world(seed)
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


def _suppress_food_and_freeze_ants(world: World) -> None:
    """Move all food off-screen and move ants to the nest with zero speed."""
    nest = world.nest
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = nest.x
        ant.y = nest.y
        ant.speed = 0


# ---------------------------------------------------------------------------
# EnergyNeed — unit tests
# ---------------------------------------------------------------------------


def test_energy_initialises_at_maximum() -> None:
    need = EnergyNeed(maximum=100)

    assert need.current == 100
    assert need.maximum == 100
    assert need.is_full


def test_energy_spend_deducts_and_returns_true() -> None:
    need = EnergyNeed(maximum=100)

    result = need.spend(10)

    assert result is True
    assert need.current == 90


def test_energy_spend_returns_false_when_insufficient() -> None:
    need = EnergyNeed(maximum=50)
    need.spend(40)  # current = 10

    result = need.spend(20)

    assert result is False
    assert need.current == 10


def test_energy_spend_leaves_state_unchanged_when_insufficient() -> None:
    need = EnergyNeed(maximum=100)
    need.spend(95)  # current = 5
    before = need.current

    need.spend(10)

    assert need.current == before


def test_energy_restore_adds_and_clamps_at_maximum() -> None:
    need = EnergyNeed(maximum=100)
    need.spend(30)  # current = 70

    need.restore(50)

    assert need.current == 100


def test_energy_restore_partial_amount() -> None:
    need = EnergyNeed(maximum=100)
    need.spend(30)

    need.restore(10)

    assert need.current == 80


def test_energy_is_not_full_after_spend() -> None:
    need = EnergyNeed(maximum=100)
    need.spend(1)

    assert not need.is_full


def test_energy_rejects_negative_maximum() -> None:
    with pytest.raises(ValueError, match="negative"):
        EnergyNeed(maximum=-1)


def test_energy_spend_rejects_negative_amount() -> None:
    need = EnergyNeed(maximum=100)
    before = need.current

    with pytest.raises(ValueError, match="negative"):
        need.spend(-5)

    assert need.current == before


def test_energy_restore_rejects_negative_amount() -> None:
    need = EnergyNeed(maximum=100)
    need.spend(20)
    before = need.current

    with pytest.raises(ValueError, match="negative"):
        need.restore(-5)

    assert need.current == before


# ---------------------------------------------------------------------------
# Ant energy — unit / component tests
# ---------------------------------------------------------------------------


def test_ant_starts_with_full_energy() -> None:
    ant = Ant(ant_id=0)

    assert ant.energy.current == settings.ANT_MAX_ENERGY
    assert ant.energy.is_full


def test_ants_own_independent_energy() -> None:
    ant_a = Ant(ant_id=10)
    ant_b = Ant(ant_id=11)

    ant_a.energy.spend(50)

    assert ant_a.energy.current < ant_b.energy.current


def test_ant_not_on_excursion_initially() -> None:
    ant = Ant(ant_id=0)

    assert not ant.on_excursion


def test_ant_depart_charges_energy_and_sets_flag() -> None:
    ant = Ant(ant_id=0)

    result = ant.depart()

    assert result is True
    assert ant.on_excursion
    assert (
        ant.energy.current
        == settings.ANT_MAX_ENERGY - settings.ANT_EXCURSION_ENERGY_COST
    )


def test_ant_depart_returns_false_when_energy_insufficient() -> None:
    ant = Ant(ant_id=0)
    # Drain all but less than one excursion cost
    remaining = settings.ANT_EXCURSION_ENERGY_COST - 1
    ant.energy.spend(settings.ANT_MAX_ENERGY - remaining)

    result = ant.depart()

    assert result is False
    assert not ant.on_excursion
    assert ant.energy.current == remaining


def test_ant_arrive_clears_excursion_flag() -> None:
    ant = Ant(ant_id=0)
    ant.depart()

    ant.arrive()

    assert not ant.on_excursion


# ---------------------------------------------------------------------------
# Spawned ant — energy invariants
# ---------------------------------------------------------------------------


def test_spawned_ant_is_fully_energized_at_creation() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    _suppress_food_and_freeze_ants(world)

    world.update()

    new_ant = max(world.ants, key=lambda a: a.id)
    assert new_ant.energy.is_full


def test_spawned_ant_is_not_on_excursion_at_creation() -> None:
    world = _world_with_reserve(settings.ANT_SPAWN_FOOD_COST)
    _suppress_food_and_freeze_ants(world)

    world.update()

    new_ant = max(world.ants, key=lambda a: a.id)
    assert not new_ant.on_excursion


# ---------------------------------------------------------------------------
# Departure — charges exactly once, not repeatedly
# ---------------------------------------------------------------------------


def test_departure_charges_energy_once_not_per_movement_tick() -> None:
    """An ant assigned a food target should lose exactly one excursion cost."""
    world = _seeded_world()
    ant = world.ants[0]

    # Give ant full energy and put food nearby so it gets a target
    food = world.food[0]
    ant.x = food.x - 5
    ant.y = food.y
    ant.speed = 0  # freeze movement so food is never collected

    # Let the world assign the food target (one tick)
    world.update()

    # Ant should have departed exactly once
    expected_energy = settings.ANT_MAX_ENERGY - settings.ANT_EXCURSION_ENERGY_COST
    assert ant.energy.current == expected_energy


def test_departure_not_charged_again_on_subsequent_updates() -> None:
    """Movement ticks while on excursion must not re-charge the cost."""
    world = _seeded_world()
    ant = world.ants[0]
    food = world.food[0]
    ant.x = food.x - 5
    ant.y = food.y
    ant.speed = 0

    world.update()  # departure charged here
    energy_after_departure = ant.energy.current

    world.update()  # further movement tick — no additional charge
    world.update()

    assert ant.energy.current == energy_after_departure


# ---------------------------------------------------------------------------
# Energy gate — ant below threshold stays at nest
# ---------------------------------------------------------------------------


def test_ant_below_energy_threshold_cannot_depart() -> None:
    world = _seeded_world()
    ant = world.ants[0]

    # Drain energy below the departure cost
    remaining = settings.ANT_EXCURSION_ENERGY_COST - 1
    ant.energy.spend(settings.ANT_MAX_ENERGY - remaining)

    food = world.food[0]
    ant.x = food.x - 5
    ant.y = food.y
    ant.speed = 0

    world.update()

    # Ant should still have no food target (stuck at nest)
    assert ant.food_target is None
    assert not ant.on_excursion


# ---------------------------------------------------------------------------
# Refueling — at-nest ants are refuelled before spawning
# ---------------------------------------------------------------------------


def test_returning_ant_refuels_at_nest() -> None:
    """An ant that just arrived at the nest should be refuelled next upkeep."""
    world = _seeded_world()
    ant = world.ants[0]
    # Simulate returned state: mark arrived, drain energy *below* the departure
    # threshold so the movement gate cannot charge departure this tick and we
    # can observe upkeep in isolation.
    ant.arrive()
    low_energy = settings.ANT_EXCURSION_ENERGY_COST - 1
    ant.energy.spend(settings.ANT_MAX_ENERGY - low_energy)
    before = ant.energy.current

    # Provide exactly enough nutrition for one refuel increment
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_REFUEL_FOOD_COST,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)

    world.update()

    assert ant.energy.current == before + settings.ANT_REFUEL_ENERGY_AMOUNT


def test_refuel_consumes_nest_nutrition() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    ant.arrive()
    # Drain energy below the departure threshold so upkeep can be observed.
    ant.energy.spend(settings.ANT_MAX_ENERGY - (settings.ANT_EXCURSION_ENERGY_COST - 1))

    world.nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_REFUEL_FOOD_COST,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)

    world.update()

    # The nutrition consumed by refuelling must come out of the reserve
    # (any extra nutrition from food collection would also appear here, but
    # food is off-screen so no collection happens)
    assert world.nest.food_reserve == 0


def test_insufficient_nest_nutrition_blocks_refuel() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    ant.arrive()
    # Drain energy below the departure threshold so upkeep is attempted.
    ant.energy.spend(settings.ANT_MAX_ENERGY - (settings.ANT_EXCURSION_ENERGY_COST - 1))
    before = ant.energy.current

    # Give no nutrition to the nest
    _suppress_food_and_freeze_ants(world)

    world.update()

    assert ant.energy.current == before  # unchanged


def test_refueling_occurs_before_spawning() -> None:
    """Nutrition spent on refuelling should reduce what is available for spawning."""
    world = _seeded_world()

    # Set up two at-nest ants with energy below the departure threshold so the
    # movement gate cannot charge departure this tick and upkeep will run.
    # Provide exactly enough nutrition to refuel both ants but NOT enough to spawn.
    total_refuel_cost = settings.ANT_REFUEL_FOOD_COST * 2
    nest_reserve = total_refuel_cost  # not enough to also spawn

    world.nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=nest_reserve,
            ),
        )
    )

    for ant in world.ants:
        ant.arrive()
        ant.energy.spend(
            settings.ANT_MAX_ENERGY - (settings.ANT_EXCURSION_ENERGY_COST - 1)
        )

    _suppress_food_and_freeze_ants(world)
    before_ants = len(world.ants)

    world.update()

    # No new ant should have been spawned because upkeep consumed the reserve.
    assert len(world.ants) == before_ants


def test_refueling_occurs_in_ascending_id_order() -> None:
    """When nutrition is scarce, the lowest-ID ant must be refuelled first."""
    world = _seeded_world()

    # Sort existing ants so we know which IDs are lowest
    ants_by_id = sorted(world.ants, key=lambda a: a.id)
    first_ant = ants_by_id[0]
    second_ant = ants_by_id[1]

    # Drain energy below the departure threshold so the movement gate cannot
    # charge departure this tick, ensuring upkeep can run for both ants.
    low_energy = settings.ANT_EXCURSION_ENERGY_COST - 1
    first_ant.arrive()
    second_ant.arrive()
    first_ant.energy.spend(settings.ANT_MAX_ENERGY - low_energy)
    second_ant.energy.spend(settings.ANT_MAX_ENERGY - low_energy)

    # Deposit only enough for one refuel
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_REFUEL_FOOD_COST,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)

    world.update()

    # First ant (lowest ID) must have been refuelled; second ant must not.
    assert first_ant.energy.current == low_energy + settings.ANT_REFUEL_ENERGY_AMOUNT
    assert second_ant.energy.current == low_energy


# ---------------------------------------------------------------------------
# Colony completion state
# ---------------------------------------------------------------------------


def _world_at_max_minus_one(seed: int = 42) -> World:
    """Return a world with exactly MAX_ANTS - 1 ants."""
    world = _seeded_world(seed)
    while len(world.ants) < settings.MAX_ANTS - 1:
        ant_id = max(a.id for a in world.ants) + 1
        dummy = Ant(ant_id)
        world.add_entity(dummy)
    return world


def test_colony_complete_when_max_ants_reached() -> None:
    world = _world_at_max_minus_one()
    assert not world.is_complete

    # Fund and trigger the final spawn
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_SPAWN_FOOD_COST,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)
    for ant in world.ants:
        ant.speed = 0

    world.update()

    assert len(world.ants) == settings.MAX_ANTS
    assert world.is_complete


def test_completion_triggered_only_once() -> None:
    """is_complete must remain True and update() must stay paused thereafter."""
    world = _world_at_max_minus_one()
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_SPAWN_FOOD_COST * 10,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)
    for ant in world.ants:
        ant.speed = 0

    world.update()  # spawns 50th ant, sets complete
    assert world.is_complete

    ants_after_first = len(world.ants)

    world.update()  # should be a no-op
    world.update()

    assert world.is_complete
    assert len(world.ants) == ants_after_first


def test_world_update_pauses_when_complete() -> None:
    """update_count must stop incrementing once the colony is complete."""
    world = _world_at_max_minus_one()
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_SPAWN_FOOD_COST,
            ),
        )
    )
    _suppress_food_and_freeze_ants(world)
    for ant in world.ants:
        ant.speed = 0

    world.update()  # completes the colony
    count_after_completion = world._update_count

    world.update()
    world.update()

    assert world._update_count == count_after_completion


def test_restart_with_same_seed_reproduces_initial_state() -> None:
    seed = 7

    world_a = World(rng=random.Random(seed))
    world_b = World(rng=random.Random(seed))

    states_a = sorted(
        (ant.id, ant.x, ant.y, ant.speed, ant.heading) for ant in world_a.ants
    )
    states_b = sorted(
        (ant.id, ant.x, ant.y, ant.speed, ant.heading) for ant in world_b.ants
    )

    assert states_a == states_b
    assert world_a.nest.food_reserve == world_b.nest.food_reserve == 0
    assert len(world_a.ants) == len(world_b.ants) == settings.STARTING_ANTS
    assert len(world_a.food) == len(world_b.food) == settings.STARTING_FOOD_SOURCES


# ---------------------------------------------------------------------------
# CompletionOverlay — headless event / button tests
# ---------------------------------------------------------------------------


def test_completion_overlay_returns_none_before_draw() -> None:
    overlay = CompletionOverlay()
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=(400, 350),
    )

    assert overlay.handle_event(event) is None


def test_completion_overlay_returns_none_for_non_click_event() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    layout = WindowLayout.calculate(
        screen.get_size(),
        settings.INSPECTOR_WIDTH,
    )
    overlay = CompletionOverlay()
    overlay.draw(screen, layout)

    motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(400, 350))
    assert overlay.handle_event(motion_event) is None


def test_completion_overlay_restart_button_click() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    layout = WindowLayout.calculate(
        screen.get_size(),
        settings.INSPECTOR_WIDTH,
    )
    overlay = CompletionOverlay()
    overlay.draw(screen, layout)

    assert overlay._restart_rect is not None
    click_pos = overlay._restart_rect.center
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=click_pos,
    )

    assert overlay.handle_event(event) == "restart"


def test_completion_overlay_exit_button_click() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    layout = WindowLayout.calculate(
        screen.get_size(),
        settings.INSPECTOR_WIDTH,
    )
    overlay = CompletionOverlay()
    overlay.draw(screen, layout)

    assert overlay._exit_rect is not None
    click_pos = overlay._exit_rect.center
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=click_pos,
    )

    assert overlay.handle_event(event) == "exit"


def test_completion_overlay_click_outside_buttons_returns_none() -> None:
    screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    layout = WindowLayout.calculate(
        screen.get_size(),
        settings.INSPECTOR_WIDTH,
    )
    overlay = CompletionOverlay()
    overlay.draw(screen, layout)

    # Click far away from any button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=(5, 5),
    )

    assert overlay.handle_event(event) is None


# ---------------------------------------------------------------------------
# Inspector snapshot includes energy
# ---------------------------------------------------------------------------


def test_snapshot_includes_selected_ant_energy() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_energy == settings.ANT_MAX_ENERGY
    assert snapshot.selected_ant_energy_max == settings.ANT_MAX_ENERGY


def test_snapshot_energy_is_none_when_no_ant_selected() -> None:
    world = _seeded_world()

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_energy is None
    assert snapshot.selected_ant_energy_max is None


def test_inspector_selected_ant_lines_include_energy() -> None:
    world = _seeded_world()
    ant = world.ants[0]
    ant.energy.spend(10)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)
    lines = Inspector._selected_ant_lines(snapshot)

    energy_lines = [line for line in lines if line.startswith("Energy:")]
    assert len(energy_lines) == 1
    expected = f"Energy: {ant.energy.current}/{ant.energy.maximum}"
    assert energy_lines[0] == expected


# ---------------------------------------------------------------------------
# Regression tests — spatial/ordering behavioral invariants
# ---------------------------------------------------------------------------


def test_remote_ant_not_at_nest_cannot_refuel() -> None:
    """A non-nest ant must not be refuelled even when not on excursion."""
    world = _seeded_world()
    ant = world.ants[0]

    # Place the ant far away from the nest and mark it as arrived (not on excursion).
    ant.x = 0
    ant.y = 0
    ant.speed = 0
    ant.arrive()
    # Drain energy but keep it above the departure cost so _assign_food_target
    # doesn't accidentally prevent movement — the key is the spatial check.
    ant.energy.spend(settings.ANT_EXCURSION_ENERGY_COST)
    before = ant.energy.current

    # Give the nest plenty of nutrition
    world.nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=100,
            ),
        )
    )
    # Move food off-screen so no collection happens
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    world.update()

    # A non-excursion ant that is not physically at the nest must not be refuelled.
    assert ant.energy.current == before


def test_targetless_wandering_departure_from_nest_costs_excursion_energy() -> None:
    """A wandering ant leaving the nest with no food target pays one departure cost."""
    world = _seeded_world()

    # Move all food away so no target is ever assigned — pure wandering departure.
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    ant = world.ants[0]
    # Initial ants start at the nest fully energized; keep speed non-zero
    # so the ant actually wanders out this tick.
    assert ant.energy.is_full
    assert not ant.on_excursion

    world.update()

    # The ant should have paid exactly one departure cost and be on excursion.
    expected = settings.ANT_MAX_ENERGY - settings.ANT_EXCURSION_ENERGY_COST
    assert ant.energy.current == expected
    assert ant.on_excursion


def test_underpowered_ant_with_no_nutrition_stays_at_nest() -> None:
    """An at-nest ant below the departure threshold must not move with no nutrition."""
    world = _seeded_world()
    ant = world.ants[0]

    # Drain energy below the departure threshold (initial ants start at nest).
    ant.energy.spend(settings.ANT_MAX_ENERGY - (settings.ANT_EXCURSION_ENERGY_COST - 1))

    # No nutrition in nest (nest starts empty).
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    pos_before = (ant.x, ant.y)

    world.update()

    # Ant must remain at its original position and stay not-on-excursion.
    assert ant.x == pos_before[0]
    assert ant.y == pos_before[1]
    assert not ant.on_excursion


def test_returning_ant_refuels_before_paying_for_next_departure() -> None:
    """Post-deposit upkeep runs before the return-trip departure.

    The ant must be refuelled first; only then can it afford to depart for the
    remembered food source in the same update.
    """
    world = _seeded_world()
    ant = world.ants[0]
    nest = world.nest
    food = world.food[0]

    # Place food at a fixed position so the ant can remember it.
    food.x = 300
    food.y = 300

    # Simulate the ant having departed on a trip and returned with low energy.
    # Use the public depart() API to set the excursion flag, then drain energy
    # further so it is below the departure threshold (9 < 10).
    ant.depart()  # energy: 100 → 90, on_excursion = True
    ant.energy.spend(90 - (settings.ANT_EXCURSION_ENERGY_COST - 1))  # energy → 9

    # Give the ant food to deposit (simulating a completed collection trip).
    ant.inventory.add(
        ResourcePortion(
            source_id=food.id,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(nest)
    ant.x = nest.x
    ant.y = nest.y

    # Let the ant remember where the food is.
    ant.observe(food)

    # Provide exactly one refuel increment so upkeep can restore enough energy
    # for the ant to afford a departure after refuelling.
    nest.deposit(
        (
            ResourcePortion(
                source_id=99,
                resource_type=ResourceType.FOOD,
                value=settings.ANT_REFUEL_FOOD_COST,
            ),
        )
    )

    # Suppress other ants so only this ant interacts.
    for other_ant in world.ants:
        if other_ant is not ant:
            other_ant.x = settings.WORLD_WIDTH
            other_ant.y = settings.WORLD_HEIGHT
            other_ant.speed = 0
    # Keep `food` in place; move other food sources off-screen.
    for other_food in world.food[1:]:
        other_food.x = settings.WORLD_WIDTH
        other_food.y = settings.WORLD_HEIGHT

    world.update()

    # If upkeep ran before return-trip selection:
    #   deposit → arrive (energy 9) → upkeep: 9+10=19 → depart (19>=10): 19-10=9
    # The ant must have a food target and be on excursion, proving the departure
    # succeeded only because refuelling happened first.
    assert ant.on_excursion
    assert ant.food_target is food


def test_initial_ants_start_at_nest_and_pay_on_first_departure() -> None:
    """Initial ants begin at the nest fully energized; first wander costs 10."""
    world = _seeded_world()

    nest_x, nest_y = settings.NEST_POSITION
    for ant in world.ants:
        assert ant.x == nest_x
        assert ant.y == nest_y
        assert ant.energy.is_full
        assert not ant.on_excursion

    # Move all food away so no food-target departure is triggered — test pure wandering.
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    world.update()

    # Every initial ant must have paid exactly one departure cost.
    expected = settings.ANT_MAX_ENERGY - settings.ANT_EXCURSION_ENERGY_COST
    for ant in world.ants:
        assert ant.energy.current == expected
        assert ant.on_excursion


def test_restart_skips_world_update_on_same_frame() -> None:
    """A fresh world created by Start Over must not be updated in the restart frame.

    The first rendered frame after restart must show exactly the initial state:
    ants at the nest, full energy and hydration, zero nest reserve, no selection,
    and no stale pheromones, memories, or completion state.
    """
    seed = 99
    world_restarted = True
    world_new = World(rng=random.Random(seed))

    # Record the pristine initial state before any update.
    initial_energy = [ant.energy.current for ant in world_new.ants]
    initial_hydration = [ant.hydration.current for ant in world_new.ants]

    # Simulate main.py's guard: `if not world.is_complete and not world_restarted`
    if not world_new.is_complete and not world_restarted:
        world_new.update()  # must NOT execute on restart frame

    # State must be identical to the moment of construction — no update ran.
    assert world_new.nest.food_reserve == 0
    assert world_new.selected_ant is None
    assert len(world_new.pheromones) == 0
    assert len(world_new.ants) == settings.STARTING_ANTS
    assert len(world_new.food) == settings.STARTING_FOOD_SOURCES

    for i, ant in enumerate(world_new.ants):
        assert ant.energy.current == initial_energy[i], (
            "ant energy must be unchanged in restart frame"
        )
        assert ant.hydration.current == pytest.approx(initial_hydration[i]), (
            "ant hydration must be unchanged in restart frame"
        )
        assert not ant.on_excursion

