import pytest

from ant_colony.components import (
    AntState,
    FoodPortion,
)
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.knowledge import EntityObservation
from ant_colony.world import World


def test_world_creates_configured_number_of_ants() -> None:
    world = World()

    assert len(world.ants) == settings.STARTING_ANTS


def test_world_contains_initial_food() -> None:
    world = World()

    assert len(world.food) == 1


def test_world_has_one_nest() -> None:
    world = World()

    assert isinstance(world.nest, Nest)


def test_entities_contains_every_world_entity() -> None:
    world = World()

    expected_count = (
        settings.STARTING_ANTS
        + len(world.food)
        + 1
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


def test_world_sensing_excludes_distant_entity() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.x = 0
    ant.y = 0
    food.x = settings.WORLD_WIDTH
    food.y = settings.SCREEN_HEIGHT

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

def test_world_assigns_closest_discovered_food() -> None:
    world = World()
    ant = world.ants[0]

    existing_food = world.food[0]
    existing_food.x = 120
    existing_food.y = 100

    farther_food = Food(
        food_id=2,
        x=130,
        y=100,
        nutrition=5,
    )
    world.add_entity(farther_food)

    ant.x = 100
    ant.y = 100
    ant.speed = 0

    world.update()

    assert ant.food_target is existing_food
    assert ant.state == AntState.SEEKING_FOOD


def test_world_collects_food_for_ant() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.x = food.x
    ant.y = food.y
    ant.speed = 0

    world.update()

    assert ant.inventory.count() == 1
    assert food.quantity == 9
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
        food_id=2,
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
        FoodPortion(
            source_id=1,
            nutrition=5,
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
        FoodPortion(
            source_id=1,
            nutrition=5,
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
        FoodPortion(
            source_id=1,
            nutrition=5,
        )
    )
    ant.select_nest_target(nest)

    world._assign_nest_target(ant)

    assert ant.nest_target is nest