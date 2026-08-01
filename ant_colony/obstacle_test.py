from ant_colony.config import settings
from ant_colony.main import main


def main_obstacle_test() -> None:
    main(
        scenario_name=settings.NAVIGATION_TEST_ARENA_NAME,
        show_grid=True,
        show_hitboxes=True,
        show_radius_overlays=True,
        window_title=f"{settings.WINDOW_TITLE} - Obstacle Test",
    )


if __name__ == "__main__":
    main_obstacle_test()
