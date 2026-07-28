from ant_colony.entities.food import Food
from ant_colony.knowledge import (
    EntityObservation,
)


def test_observation_is_created_from_entity() -> None:
    food = Food(
        food_id=7,
        x=120,
        y=240,
        nutrition=5,
    )

    observation = (
        EntityObservation.from_entity(food)
    )

    assert observation.entity_id == 7
    assert observation.entity_type == "food"
    assert observation.position == (
        120,
        240,
    )


def test_observation_has_unique_memory_name() -> None:
    observation = EntityObservation(
        entity_id=7,
        entity_type="food",
        x=120,
        y=240,
    )

    assert (
        observation.memory_name
        == "entity:food:7"
    )