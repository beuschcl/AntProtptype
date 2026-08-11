from __future__ import annotations

from collections.abc import Callable

from ant_colony.config import settings
from ant_colony.geometry import RectangleObstacle


class CollisionMap:
    """Answers geometry questions for obstacle-aware systems."""

    def __init__(
        self,
        obstacles: Callable[[], tuple[RectangleObstacle, ...]],
    ) -> None:
        self._obstacles = obstacles

    @property
    def obstacles(self) -> tuple[RectangleObstacle, ...]:
        return self._obstacles()

    def movement_intersects_obstacle(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        radius: float = 0.0,
    ) -> bool:
        padding = max(0.0, radius - settings.COLLISION_TANGENT_EPSILON)
        return any(
            obstacle.intersects_segment(
                start,
                end,
                padding=padding,
            )
            for obstacle in self.obstacles
        )

    def position_is_blocked(
        self,
        x: float,
        y: float,
        *,
        radius: float = 0.0,
    ) -> bool:
        collision_radius = max(
            0.0,
            radius - settings.COLLISION_TANGENT_EPSILON,
        )
        return any(
            obstacle.intersects_circle(
                x,
                y,
                collision_radius,
            )
            for obstacle in self.obstacles
        )

    def line_of_sight_is_blocked(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> bool:
        return self.movement_intersects_obstacle(start, end)
