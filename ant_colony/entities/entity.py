from __future__ import annotations

import math

from ant_colony.graphics.primitives import Shape


class Entity:
    def __init__(
        self,
        entity_id: int | str,
        x: float,
        y: float,
        discoverable_radius: float,
    ) -> None:
        self.id = entity_id
        self.x = x
        self.y = y
        self.discoverable_radius = discoverable_radius

    def update(self) -> None:
        """Advance the entity by one simulation step."""

    def distance_to(self, other: Entity) -> float:
        return self.distance_to_position(
            other.x,
            other.y,
        )

    def distance_to_position(
        self,
        x: float,
        y: float,
    ) -> float:
        return math.hypot(
            self.x - x,
            self.y - y,
        )

    def shapes(self) -> tuple[Shape, ...]:
        return ()

    @property
    def hitbox_radius(self) -> float:
        return 0.0

    def intersects_position(
        self,
        x: float,
        y: float,
        *,
        padding: float = 0.0,
    ) -> bool:
        return (
            self.distance_to_position(x, y)
            <= self.hitbox_radius + padding
        )

    def intersects_entity(
        self,
        other: Entity,
        *,
        padding: float = 0.0,
    ) -> bool:
        return self.distance_to(other) <= (
            self.hitbox_radius
            + other.hitbox_radius
            + padding
        )