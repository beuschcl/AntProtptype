from ant_colony.config import settings
from ant_colony.main import main


def main_route_reassessment_test() -> None:
    main(
        scenario_name=settings.ROUTE_REASSESSMENT_ARENA_NAME,
        show_grid=True,
        show_hitboxes=True,
        show_radius_overlays=True,
        window_title=f"{settings.WINDOW_TITLE} - Route Reassessment Test",
    )


if __name__ == "__main__":
    main_route_reassessment_test()
