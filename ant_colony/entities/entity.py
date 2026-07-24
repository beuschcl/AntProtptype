#entities/entity.py
from __future__ import annotations

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

    def distance_to(self, other: Entity) -> float:
        dx = self.x - other.x
        dy = self.y - other.y

        return (dx * dx + dy * dy) ** 0.5

    def shapes(self) -> tuple[Shape, ...]:
        return ()