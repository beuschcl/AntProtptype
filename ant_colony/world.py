import math

from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest


class World:
    def __init__(self) -> None:
        self.nest = Nest(
            x=settings.WORLD_WIDTH / 2,
            y=settings.SCREEN_HEIGHT / 2,
        )

        self.ants = [
            Ant(ant_id)
            for ant_id in range(settings.STARTING_ANTS)
        ]

        self.food = [
            Food(
                food_id=1,
                x=200,
                y=200,
                nutrition=5,
            ),
        ]

        self.selected_ant: Ant | None = None

    def update(self) -> None:
        for ant in self.ants:
            ant.update()

    def handle_click(self, position: tuple[float, float]) -> None:
        mouse_x, mouse_y = position

        if not self._is_inside_world(mouse_x, mouse_y):
            self.selected_ant = None
            return

        closest_ant: Ant | None = None
        closest_distance = settings.CLICK_RADIUS

        for ant in self.ants:
            distance = math.hypot(
                ant.x - mouse_x,
                ant.y - mouse_y,
            )

            if distance < closest_distance:
                closest_ant = ant
                closest_distance = distance

        self.selected_ant = closest_ant

    @staticmethod
    def _is_inside_world(x: float, y: float) -> bool:
        return (
            0 <= x <= settings.WORLD_WIDTH
            and 0 <= y <= settings.SCREEN_HEIGHT
        )

    def __repr__(self) -> str:
        return (
            f"World("
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}"
            f")"
        )