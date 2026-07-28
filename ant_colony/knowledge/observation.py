from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ant_colony.entities.entity import Entity


@dataclass(frozen=True, slots=True)
class EntityObservation:
    entity_id: int | str
    entity_type: str
    x: float
    y: float

    @classmethod
    def from_entity(
        cls,
        entity: Entity,
    ) -> EntityObservation:
        return cls(
            entity_id=entity.id,
            entity_type=type(entity).__name__.lower(),
            x=entity.x,
            y=entity.y,
        )

    @property
    def memory_name(self) -> str:
        return f"entity:{self.entity_type}:{self.entity_id}"

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y
