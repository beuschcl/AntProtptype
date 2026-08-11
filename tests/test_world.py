import pytest

from ant_colony.components import (
    AntState,
    FoodTargetSource,
    ResourcePortion,
    ResourceType,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.entities.pheromone import Pheromone, PheromoneType
from ant_colony.entities.resource import Resource
from ant_colony.geometry import RectangleObstacle
from ant_colony.knowledge import EntityObservation
from ant_colony.scenarios import Scenario
from ant_colony.world import World


def test_world_creates_configured_number_of_ants() -> None:
    world = World()

    assert len(world.ants) == settings.STARTING_ANTS


def test_world_contains_initial_food() -> None:
    world = World()

    assert len(world.food) == settings.STARTING_FOOD_SOURCES


def _world_with_food_sources(count: int) -> World:
    world = World()

    while len(world.food) < count:
        food_index = len(world.food)
        world.add_entity(
            Food(
                food_id=100 + food_index,
                x=100 + food_index * 80,
                y=100,
                nutrition=settings.FOOD_NUTRITION,
            )
        )

    return world


def test_world_has_one_nest() -> None:
    world = World()

    assert isinstance(world.nest, Nest)
    assert (world.nest.x, world.nest.y) == settings.NEST_POSITION


def test_entities_contains_every_world_entity() -> None:
    world = World()

    expected_count = (
        len(world.ants)
        + 1
        + len(world.food)
    )

    assert len(world.entities) == expected_count


def test_entities_property_is_read_only() -> None:
    world = World()

    assert isinstance(world.entities, tuple)


def test_world_can_add_entity() -> None:
    world = World()
    food = Food(
        food_id=2,
        x=300,
        y=300,
        nutrition=10,
    )

    world.add_entity(food)

    assert food in world.entities
    assert food in world.food


def test_world_rejects_same_entity_twice() -> None:
    world = World()
    food = Food(
        food_id=2,
        x=300,
        y=300,
        nutrition=10,
    )

    world.add_entity(food)

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        world.add_entity(food)


def test_world_can_remove_entity() -> None:
    world = World()
    food = world.food[0]

    world.remove_entity(food)

    assert food not in world.entities
    assert food not in world.food


def test_world_rejects_removal_of_unknown_entity() -> None:
    world = World()
    unknown_entity = Food(
        food_id=99,
        x=0,
        y=0,
        nutrition=1,
    )

    with pytest.raises(
        ValueError,
        match="not registered",
    ):
        world.remove_entity(unknown_entity)


def test_removing_selected_ant_clears_selection() -> None:
    world = World()
    ant = world.ants[0]
    world.selected_ant = ant

    world.remove_entity(ant)

    assert world.selected_ant is None


def test_entities_can_be_filtered_by_type() -> None:
    world = World()

    ants = world.entities_of_type(Ant)
    food = world.entities_of_type(Food)

    assert ants == world.ants
    assert food == world.food


def test_world_updates_registered_entities() -> None:
    class UpdatingEntity(Entity):
        def __init__(self) -> None:
            super().__init__(
                entity_id="updating-entity",
                x=0,
                y=0,
                discoverable_radius=0,
            )
            self.update_count = 0

        def update(self) -> None:
            self.update_count += 1

    world = World()
    entity = UpdatingEntity()
    world.add_entity(entity)

    world.update()

    assert entity.update_count == 1


def test_click_outside_world_clears_selection() -> None:
    world = World()
    world.selected_ant = world.ants[0]

    world.handle_click(
        (
            settings.WORLD_WIDTH + 10,
            100,
        )
    )

    assert world.selected_ant is None


def test_click_near_ant_selects_ant() -> None:
    world = World()
    ant = world.ants[0]
    ant.x = 100
    ant.y = 100

    world.handle_click((100, 100))

    assert world.selected_ant is ant


def test_world_finds_entity_under_position() -> None:
    world = World()
    ant = world.ants[0]
    ant.x = 120
    ant.y = 140

    hovered = world.entity_under_position((120, 140))

    assert hovered is ant

def test_world_coordinates_ant_sensing() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.x = 100
    ant.y = 100
    food.x = 100
    food.y = 100

    discovered = world.sense_for(ant)

    assert food in discovered

    observation = ant.knowledge.recall(
        f"entity:food:{food.id}"
    )

    assert isinstance(
        observation,
        EntityObservation,
    )
    assert observation.position == (
        100,
        100,
    )
    assert food.is_discovered


def test_world_sensing_excludes_distant_entity() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.x = 0
    ant.y = 0
    food.x = settings.WORLD_WIDTH
    food.y = settings.WORLD_HEIGHT

    discovered = world.sense_for(ant)

    assert food not in discovered
    assert not ant.knowledge.knows(
        f"entity:food:{food.id}"
    )


def test_world_sensing_excludes_ant_itself() -> None:
    world = World()
    ant = world.ants[0]

    discovered = world.sense_for(ant)

    assert ant not in discovered


def test_world_rejects_sensing_for_unregistered_ant() -> None:
    world = World()
    unknown_ant = Ant(ant_id=999)

    with pytest.raises(
        ValueError,
        match="not registered",
    ):
        world.sense_for(unknown_ant)


def test_world_sensing_does_not_detect_food_through_wall() -> None:
    scenario = Scenario(
        name="wall_occluded_food",
        nest_position=(100, 100),
        initial_food_positions=((155, 100),),
        obstacles=(
            RectangleObstacle(
                x=125,
                y=60,
                width=20,
                height=80,
            ),
        ),
    )
    world = World(scenario=scenario)
    ant = world.ants[0]
    food = world.food[0]

    discovered = world.sense_for(ant)

    assert food not in discovered
    assert not food.is_discovered
    assert not ant.knowledge.knows(
        f"entity:food:{food.id}"
    )


def test_world_prefers_visible_food_over_closer_wall_occluded_food() -> None:
    scenario = Scenario(
        name="visible_food_beats_occluded_food",
        nest_position=(100, 100),
        initial_food_positions=((155, 100),),
        obstacles=(
            RectangleObstacle(
                x=125,
                y=60,
                width=20,
                height=80,
            ),
        ),
    )
    world = World(scenario=scenario)
    ant = world.ants[0]
    hidden_food = world.food[0]
    visible_food = Food(
        food_id=9998,
        x=100,
        y=165,
        nutrition=5,
    )
    world.add_entity(visible_food)

    discovered = world.sense_for(ant)
    world._assign_food_target(ant, discovered)

    assert hidden_food not in discovered
    assert visible_food in discovered
    assert ant.food_target is visible_food
    assert ant.food_target_source == FoodTargetSource.DISCOVERY


def test_world_assigns_closest_discovered_food() -> None:
    world = World()
    ant = world.ants[0]
    collect_boundary = (
        ant.hitbox_radius
        + settings.FOOD_RADIUS
        + settings.ANT_INTERACTION_RADIUS
    )

    existing_food = world.food[0]
    existing_food.x = 100 + collect_boundary + 8
    existing_food.y = 100

    farther_food = Food(
        food_id=9998,
        x=100 + collect_boundary + 18,
        y=100,
        nutrition=5,
    )
    world.add_entity(farther_food)

    ant.x = 100
    ant.y = 100
    ant.speed = 0

    world.update()

    assert ant.food_target is existing_food
    assert ant.food_target_source == FoodTargetSource.DISCOVERY
    assert ant.state == AntState.SEEKING_FOOD


def test_world_assigns_food_from_personal_memory() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 100
    ant.y = 100
    food.x = settings.WORLD_WIDTH
    food.y = settings.WORLD_HEIGHT
    ant.observe(food)

    world._assign_food_target(ant, ())

    assert ant.food_target is food
    assert ant.food_target_source == FoodTargetSource.MEMORY
    assert ant.state == AntState.SEEKING_FOOD


def test_world_prefers_new_discovery_over_remembered_food() -> None:
    world = _world_with_food_sources(2)
    ant = world.ants[0]
    remembered_food = world.food[0]
    discovered_food = world.food[1]
    ant.observe(remembered_food)

    world._assign_food_target(
        ant,
        (discovered_food,),
    )

    assert ant.food_target is discovered_food
    assert ant.food_target_source == FoodTargetSource.DISCOVERY


def test_world_assigns_food_from_sensed_pheromone() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)
    ant.x = 100
    ant.y = 100

    world._assign_food_target(
        ant,
        (pheromone,),
    )

    assert ant.food_target is food
    assert ant.food_target_source == FoodTargetSource.PHEROMONE
    assert ant.state == AntState.SEEKING_FOOD


def test_world_does_not_recruit_ant_outside_pheromone_range() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=food.id,
        x=settings.WORLD_WIDTH,
        y=settings.WORLD_HEIGHT,
    )
    world.add_entity(pheromone)
    ant.x = 0
    ant.y = 0
    food.x = settings.WORLD_WIDTH
    food.y = settings.WORLD_HEIGHT

    discovered = world.sense_for(ant)
    world._assign_food_target(ant, discovered)

    assert pheromone not in discovered
    assert ant.food_target is None
    assert ant.state == AntState.WANDERING


def test_world_prefers_discovered_food_over_pheromone() -> None:
    world = _world_with_food_sources(2)
    ant = world.ants[0]
    discovered_food = world.food[0]
    pheromone_food = world.food[1]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=pheromone_food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)

    world._assign_food_target(
        ant,
        (
            pheromone,
            discovered_food,
        ),
    )

    assert ant.food_target is discovered_food
    assert ant.food_target_source == FoodTargetSource.DISCOVERY


def test_world_prefers_pheromone_over_remembered_food() -> None:
    world = _world_with_food_sources(2)
    ant = world.ants[0]
    remembered_food = world.food[0]
    pheromone_food = world.food[1]
    ant.observe(remembered_food)
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=pheromone_food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)

    world._assign_food_target(
        ant,
        (pheromone,),
    )

    assert ant.food_target is pheromone_food
    assert ant.food_target_source == FoodTargetSource.PHEROMONE


def test_world_selects_strongest_pheromone_then_lowest_id() -> None:
    world = _world_with_food_sources(2)
    ant = world.ants[0]
    first_food = world.food[0]
    second_food = world.food[1]
    strong_pheromone = Pheromone(
        pheromone_id=5,
        source_food_id=first_food.id,
        x=100,
        y=100,
        strength=0.8,
    )
    weak_pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=second_food.id,
        x=100,
        y=100,
        strength=0.2,
    )

    world._assign_food_target(
        ant,
        (
            weak_pheromone,
            strong_pheromone,
        ),
    )

    assert ant.food_target is first_food
    assert ant.food_target_source == FoodTargetSource.PHEROMONE

    ant.clear_food_target()

    equal_strength_a = Pheromone(
        pheromone_id=3,
        source_food_id=first_food.id,
        x=100,
        y=100,
        strength=0.6,
    )
    equal_strength_b = Pheromone(
        pheromone_id=2,
        source_food_id=second_food.id,
        x=100,
        y=100,
        strength=0.6,
    )

    world._assign_food_target(
        ant,
        (
            equal_strength_a,
            equal_strength_b,
        ),
    )

    assert ant.food_target is second_food
    assert ant.food_target_source == FoodTargetSource.PHEROMONE


def test_world_ignores_pheromone_for_missing_food_source() -> None:
    world = World()
    ant = world.ants[0]
    missing_food = world.food[0]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=missing_food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)
    world.remove_entity(missing_food)

    world._assign_food_target(
        ant,
        (pheromone,),
    )

    assert ant.food_target is None
    assert ant.state == AntState.WANDERING


def test_world_forgets_food_that_is_no_longer_available() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    observation = ant.observe(food)
    world.remove_entity(food)

    world._assign_food_target(ant, ())

    assert not ant.knowledge.knows(observation.memory_name)
    assert ant.food_target is None
    assert ant.state == AntState.WANDERING


def test_ant_stops_returning_when_remembered_food_is_exhausted() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    observation = ant.observe(food)

    while not food.is_depleted:
        food.collect()

    world._remove_depleted_resources()
    world._assign_food_target(ant, ())

    assert food not in world.food
    assert not ant.knowledge.knows(observation.memory_name)
    assert ant.food_target is None
    assert ant.state == AntState.WANDERING


def test_ant_returns_to_remembered_food_after_delivery() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    nest = world.nest
    food.x = 200
    food.y = 200
    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    for other_ant in world.ants[1:]:
        other_ant.x = settings.WORLD_WIDTH
        other_ant.y = settings.WORLD_HEIGHT
        other_ant.speed = 0

    for other_food in world.food[1:]:
        other_food.x = settings.WORLD_WIDTH
        other_food.y = settings.WORLD_HEIGHT

    world.update()

    assert ant.inventory.count() == settings.ANT_FOOD_PICKUP_AMOUNT
    assert ant.state == AntState.CARRYING_FOOD

    ant.x = nest.x
    ant.y = nest.y

    world.update()

    assert ant.inventory.is_empty
    assert ant.food_target is food
    assert ant.food_target_source == FoodTargetSource.MEMORY
    assert ant.state == AntState.SEEKING_FOOD


def test_world_collects_food_for_ant() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    for other_ant in world.ants[1:]:
        other_ant.x = 0
        other_ant.y = 0
        other_ant.speed = 0

    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    world.update()

    assert ant.inventory.count() == settings.ANT_FOOD_PICKUP_AMOUNT
    assert food.quantity == 10 - settings.ANT_FOOD_PICKUP_AMOUNT
    assert ant.state == AntState.CARRYING_FOOD


def test_world_removes_depleted_food() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    while food.quantity > 1:
        food.collect()

    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    world.update()

    assert food not in world.entities
    assert food not in world.food


def test_removing_food_clears_ant_target() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.select_food_target(food)

    world.remove_entity(food)

    assert ant.food_target is None
    assert ant.food_target_source is None
    assert ant.state == AntState.WANDERING


def test_full_ant_does_not_select_more_food() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    world.update()

    second_food = Food(
        food_id=9999,
        x=ant.x,
        y=ant.y,
        nutrition=5,
    )
    world.add_entity(second_food)

    world.update()

    assert ant.food_target is None
    assert ant.state == AntState.CARRYING_FOOD
    assert second_food.quantity == 1

def test_world_assigns_nest_to_carrying_ant() -> None:
    world = World()
    ant = world.ants[0]

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.state = AntState.CARRYING_FOOD

    world._assign_nest_target(ant)

    assert ant.nest_target is world.nest


def test_world_deposits_food_at_nest() -> None:
    world = World()
    ant = world.ants[0]
    nest = world.nest

    ant.x = nest.x
    ant.y = nest.y

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(nest)

    world._deposit_food_for(ant)

    assert ant.inventory.is_empty
    assert nest.food_reserve == 5
    assert ant.state == AntState.WANDERING


def test_world_does_not_replace_existing_nest_target() -> None:
    world = World()
    ant = world.ants[0]
    nest = world.nest

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(nest)

    world._assign_nest_target(ant)

    assert ant.nest_target is nest

def test_world_exposes_pheromones() -> None:
    world = World()

    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=1,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)

    assert world.pheromones == (pheromone,)


def test_world_deposits_pheromone_for_carrying_ant() -> None:
    world = World()
    ant = world.ants[0]
    for other_ant in world.ants[1:]:
        other_ant.x = 0
        other_ant.y = 0
        other_ant.speed = 0
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    ant.x = 100
    ant.y = 200
    ant.speed = 0

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(world.nest)

    world.update()

    assert len(world.pheromones) == 1

    pheromone = world.pheromones[0]

    assert pheromone.source_food_id == 1
    assert pheromone.pheromone_type == PheromoneType.FOOD
    assert pheromone.x == 100
    assert pheromone.y == 200


def test_world_deposits_explore_pheromone_for_wandering_ant() -> None:
    world = World()
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    world.update()

    assert len(world.pheromones) == len(world.ants)
    assert all(
        pheromone.pheromone_type == PheromoneType.EXPLORE
        for pheromone in world.pheromones
    )
    assert all(
        pheromone.source_food_id is None
        for pheromone in world.pheromones
    )


def test_world_deposits_food_pheromone_for_ant_seeking_food() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]
    ant.x = 100
    ant.y = 200
    ant.speed = 0
    ant.select_food_target(food)

    world.update()

    assert len(world.pheromones) == 1
    pheromone = world.pheromones[0]
    assert pheromone.pheromone_type == PheromoneType.FOOD
    assert pheromone.source_food_id == food.id
    assert pheromone.x == 100
    assert pheromone.y == 200


def test_world_respects_pheromone_deposit_interval() -> None:
    world = World()
    ant = world.ants[0]
    for other_ant in world.ants[1:]:
        other_ant.x = 0
        other_ant.y = 0
        other_ant.speed = 0
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT

    ant.x = 100
    ant.y = 200
    ant.speed = 0

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(world.nest)

    world.update()
    initial_count = len(world.pheromones)

    world.update()

    assert initial_count == 1
    assert len(world.pheromones) == 1


def test_world_removes_depleted_pheromone() -> None:
    world = World()
    for food in world.food:
        food.x = settings.WORLD_WIDTH
        food.y = settings.WORLD_HEIGHT
    for ant in world.ants:
        ant.x = 0
        ant.y = 0
        ant.speed = 0

    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=1,
        x=100,
        y=100,
        strength=(
            settings.PHEROMONE_EVAPORATION_RATE / 2
        ),
    )
    world.add_entity(pheromone)

    world.update()

    assert pheromone not in world.entities
    assert pheromone not in world.pheromones


def test_world_keeps_pheromones_when_source_food_is_removed() -> None:
    world = World()
    food = world.food[0]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)

    world.remove_entity(food)

    assert pheromone in world.entities
    assert pheromone in world.pheromones


def test_world_keeps_pheromones_when_source_food_is_depleted() -> None:
    world = World()
    food = world.food[0]
    pheromone = Pheromone(
        pheromone_id=1,
        source_food_id=food.id,
        x=100,
        y=100,
    )
    world.add_entity(pheromone)

    while not food.is_depleted:
        food.collect()

    world._remove_depleted_resources()

    assert food not in world.food
    assert pheromone in world.entities
    assert pheromone in world.pheromones
    assert pheromone.source_food_id == food.id

def test_world_exposes_food_resources() -> None:
    world = World()

    assert len(world.food) == settings.STARTING_FOOD_SOURCES

    assert all(
        isinstance(resource, Resource)
        for resource in world.resources
    )
