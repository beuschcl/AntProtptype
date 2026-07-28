from collections.abc import Iterable

from ant_colony.config import settings
from ant_colony.entities.entity import Entity


class Senses:
    def __init__(
        self,
        radius: float = settings.ANT_SENSE_RADIUS,
    ) -> None:
        if radius < 0:
            raise ValueError("Sense radius cannot be negative.")

        self.radius = radius

    def can_detect(
        self,
        observer: Entity,
        target: Entity,
    ) -> bool:
        if observer is target:
            return False

        detection_distance = self.radius + target.discoverable_radius

        return observer.distance_to(target) <= detection_distance

    def detect(
        self,
        observer: Entity,
        candidates: Iterable[Entity],
    ) -> tuple[Entity, ...]:
        return tuple(
            candidate
            for candidate in candidates
            if self.can_detect(
                observer,
                candidate,
            )
        )
