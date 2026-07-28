from ant_colony.components import (
    AntState,
    FoodTargetSource,
    ResourcePortion,
    ResourceType,
)
from ant_colony.entities.pheromone import Pheromone
from ant_colony.ui.inspector_snapshot import (
    InspectorSnapshot,
)
from ant_colony.world import World


def test_snapshot_contains_colony_summary() -> None:
    world = World()

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.ant_count == len(world.ants)
    assert snapshot.food_source_count == len(world.food)
    assert snapshot.remaining_food_portions == sum(food.quantity for food in world.food)
    assert snapshot.nest_food_reserve == 0
    assert snapshot.delivered_portions == 0
    assert snapshot.selected_ant_id is None
    assert snapshot.pheromone_count == 0


def test_snapshot_contains_nest_delivery_totals() -> None:
    world = World()

    world.nest.deposit(
        (
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=5,
            ),
            ResourcePortion(
                source_id=1,
                resource_type=ResourceType.FOOD,
                value=5,
            ),
        )
    )

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.nest_food_reserve == 10
    assert snapshot.delivered_portions == 2


def test_snapshot_contains_selected_ant_details() -> None:
    world = World()
    ant = world.ants[0]

    ant.x = 100
    ant.y = 200
    ant.speed = 1.25
    ant.heading = 90
    ant.state = AntState.WANDERING

    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_id == ant.id
    assert snapshot.selected_ant_x == 100
    assert snapshot.selected_ant_y == 200
    assert snapshot.selected_ant_speed == 1.25
    assert snapshot.selected_ant_heading == 90
    assert snapshot.selected_ant_state == "wandering"
    assert snapshot.selected_ant_inventory_count == 0
    assert snapshot.selected_ant_inventory_capacity == 2
    assert snapshot.remaining_food_portions == sum(food.quantity for food in world.food)
    assert snapshot.selected_ant_target == "None"


def test_snapshot_identifies_food_target() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.select_food_target(food)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == (f"Food {food.id}")


def test_snapshot_explains_remembered_food_target() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.select_food_target(
        food,
        source=FoodTargetSource.MEMORY,
    )
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == (f"Food {food.id} (remembered)")


def test_snapshot_explains_pheromone_food_target() -> None:
    world = World()
    ant = world.ants[0]
    food = world.food[0]

    ant.select_food_target(
        food,
        source=FoodTargetSource.PHEROMONE,
    )
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == (f"Food {food.id} (pheromone)")


def test_snapshot_identifies_nest_target() -> None:
    world = World()
    ant = world.ants[0]

    ant.inventory.add(
        ResourcePortion(
            source_id=1,
            resource_type=ResourceType.FOOD,
            value=5,
        )
    )
    ant.select_nest_target(world.nest)
    world.selected_ant = ant

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.selected_ant_target == "Nest"
    assert snapshot.selected_ant_inventory_count == 1


def test_snapshot_contains_pheromone_count() -> None:
    world = World()

    world.add_entity(
        Pheromone(
            pheromone_id=1,
            source_food_id=1,
            x=100,
            y=100,
        )
    )
    world.add_entity(
        Pheromone(
            pheromone_id=2,
            source_food_id=1,
            x=200,
            y=200,
        )
    )

    snapshot = InspectorSnapshot.from_world(world)

    assert snapshot.pheromone_count == 2
