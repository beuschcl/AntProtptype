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