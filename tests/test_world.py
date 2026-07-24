import pytest

from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
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