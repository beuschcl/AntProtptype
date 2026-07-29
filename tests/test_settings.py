from ant_colony.config import settings


def test_requested_visual_palette_constants() -> None:
    assert settings.FOOD_COLOR == (90, 220, 90)
    assert settings.FOOD_OUTLINE_COLOR == (20, 55, 25)
    assert settings.NEST_COLOR == (244, 174, 66)
    assert settings.NEST_OUTLINE_COLOR == (70, 38, 12)
    assert settings.PHEROMONE_COLOR == (215, 80, 255)
    assert settings.DEBUG_HITBOX_COLOR == (0, 255, 255)
    assert settings.DEBUG_ANT_DISCOVERY_RADIUS_COLOR == (255, 215, 0)
    assert settings.DEBUG_FOOD_DISCOVERY_RADIUS_COLOR == (120, 255, 120)
    assert settings.DEBUG_NEST_DISCOVERY_RADIUS_COLOR == (255, 150, 70)
    assert settings.DEBUG_PHEROMONE_DISCOVERY_RADIUS_COLOR == (235, 115, 255)
    assert settings.DEBUG_SENSE_RADIUS_COLOR == (173, 216, 230)
    assert settings.DEBUG_INTERACTION_RADIUS_COLOR == (255, 120, 200)


def test_debug_grid_spacing_is_100() -> None:
    assert settings.DEBUG_GRID_SPACING == 100