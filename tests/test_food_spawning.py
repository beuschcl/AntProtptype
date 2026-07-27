import random

from ant_colony.config import settings
from ant_colony.entities.building_material import BuildingMaterial
from ant_colony.entities.water import Water
from ant_colony.world import World


def _seeded_world(seed: int = 42) -> World:
    return World(rng=random.Random(seed))


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_world_creates_configured_number_of_food_sources() -> None:
    world = _seeded_world()

    assert len(world.food) == settings.STARTING_FOOD_SOURCES


def test_initial_food_positions_are_deterministic_with_seeded_rng() -> None:
    world_a = _seeded_world(seed=7)
    world_b = _seeded_world(seed=7)

    positions_a = [(f.x, f.y) for f in world_a.food]
    positions_b = [(f.x, f.y) for f in world_b.food]

    assert positions_a == positions_b


def test_different_seeds_produce_different_layouts() -> None:
    world_a = _seeded_world(seed=1)
    world_b = _seeded_world(seed=2)

    positions_a = [(f.x, f.y) for f in world_a.food]
    positions_b = [(f.x, f.y) for f in world_b.food]

    assert positions_a != positions_b


def test_every_food_source_is_inside_world_bounds() -> None:
    world = _seeded_world()

    for food in world.food:
        assert food.x - settings.FOOD_RADIUS >= 0
        assert food.x + settings.FOOD_RADIUS <= settings.WORLD_WIDTH
        assert food.y - settings.FOOD_RADIUS >= 0
        assert food.y + settings.FOOD_RADIUS <= settings.SCREEN_HEIGHT


def test_initial_food_ids_are_unique() -> None:
    world = _seeded_world()

    ids = [food.id for food in world.food]

    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Depletion → replenishment
# ---------------------------------------------------------------------------


def test_depleting_food_removes_it_and_spawns_one_replacement() -> None:
    world = _seeded_world()
    food = world.food[0]

    # Drain all portions except the last one
    while food.quantity > 1:
        food.collect()

    # Collect the last portion via the world update cycle
    ant = world.ants[0]
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    world.update()

    assert food not in world.entities
    assert food not in world.food
    assert len(world.food) == settings.STARTING_FOOD_SOURCES


def test_food_count_stays_constant_after_depletion() -> None:
    world = _seeded_world()
    initial_count = len(world.food)

    food = world.food[0]
    while food.quantity > 1:
        food.collect()

    ant = world.ants[0]
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    world.update()

    assert len(world.food) == initial_count


def test_replacement_food_has_a_new_unique_id() -> None:
    world = _seeded_world()
    original_ids = {f.id for f in world.food}
    food = world.food[0]

    while food.quantity > 1:
        food.collect()

    ant = world.ants[0]
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0
    world.update()

    new_ids = {f.id for f in world.food}
    replacement_ids = new_ids - (original_ids - {food.id})

    assert len(replacement_ids) == 1
    new_id = next(iter(replacement_ids))
    assert new_id not in original_ids


# ---------------------------------------------------------------------------
# Other resource types must NOT trigger food spawning
# ---------------------------------------------------------------------------


def test_depleting_water_does_not_spawn_food() -> None:
    world = _seeded_world()
    initial_food_count = len(world.food)

    water = Water(
        water_id=999,
        x=100,
        y=100,
        hydration=3,
        quantity=1,
    )
    world.add_entity(water)
    water.collect()
    world.update()

    assert water not in world.entities
    assert len(world.food) == initial_food_count


def test_depleting_building_material_does_not_spawn_food() -> None:
    world = _seeded_world()
    initial_food_count = len(world.food)

    material = BuildingMaterial(
        material_id=999,
        x=100,
        y=100,
        construction_value=2,
        quantity=1,
    )
    world.add_entity(material)
    material.collect()
    world.update()

    assert material not in world.entities
    assert len(world.food) == initial_food_count


# ---------------------------------------------------------------------------
# Manual removal must NOT trigger replenishment
# ---------------------------------------------------------------------------


def test_manually_removing_non_depleted_food_does_not_spawn_replacement() -> None:
    world = _seeded_world()
    initial_count = len(world.food)
    food = world.food[0]

    # food is NOT depleted
    assert not food.is_depleted

    world.remove_entity(food)

    # No replacement should have been added
    assert len(world.food) == initial_count - 1
