from ant_colony.config import settings
from ant_colony.main import main


def main_maze_pheromone_test() -> None:
    main(
        scenario_name=settings.MAZE_PHEROMONE_ARENA_NAME,
        show_grid=True,
        show_hitboxes=True,
        show_radius_overlays=True,
        window_title=f"{settings.WINDOW_TITLE} - Maze Pheromone Test",
    )


if __name__ == "__main__":
    main_maze_pheromone_test()
