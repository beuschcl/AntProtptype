#tests/test_world.py
from ant_colony.config import settings
from ant_colony.world import World


def test_world_creates_configured_number_of_ants() -> None:
    world = World()

    assert len(world.ants) == settings.STARTING_ANTS


def test_world_contains_initial_food() -> None:
    world = World()

    assert len(world.food) == 1


def test_world_has_a_nest() -> None:
    world = World()

    assert world.nest is not None