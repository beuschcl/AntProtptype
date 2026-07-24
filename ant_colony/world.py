from collections.abc import Iterator
from typing import TypeVar

from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest

EntityType = TypeVar("EntityType", bound=Entity)


class World:
    def __init__(self) -> None:
        self._entities: list[Entity] = []
        self.selected_ant: Ant | None = None

        self.add_entity(
            Nest(
                x=settings.WORLD_WIDTH / 2,
                y=settings.SCREEN_HEIGHT / 2,
            )
        )

        for ant_id in range(settings.STARTING_ANTS):
            self.add_entity(Ant(ant_id))

        self.add_entity(
            Food(
                food_id=1,
                x=200,
                y=200,
                nutrition=5,
            )
        )

    @property
    def entities(self) -> tuple[Entity, ...]:
        return tuple(self._entities)

    @property
    def ants(self) -> tuple[Ant, ...]:
        return self.entities_of_type(Ant)

    @property
    def food(self) -> tuple[Food, ...]:
        return self.entities_of_type(Food)

    @property
    def nest(self) -> Nest:
        nests = self.entities_of_type(Nest)

        if len(nests) != 1:
            raise RuntimeError(
                "World must contain exactly one nest. "
                f"Found {len(nests)}."
            )

        return nests[0]

    def add_entity(self, entity: Entity) -> None:
        if entity in self._entities:
            raise ValueError(
                "The entity is already registered with this world."
            )

        self._entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        try:
            self._entities.remove(entity)
        except ValueError as error:
            raise ValueError(
                "The entity is not registered with this world."
            ) from error

        if entity is self.selected_ant:
            self.selected_ant = None

    def entities_of_type(
        self,
        entity_type: type[EntityType],
    ) -> tuple[EntityType, ...]:
        return tuple(
            entity
            for entity in self._entities
            if isinstance(entity, entity_type)
        )

    def __iter__(self) -> Iterator[Entity]:
        return iter(self._entities)

    def update(self) -> None:
        for entity in tuple(self._entities):
            entity.update()

    def handle_click(self, position: tuple[float, float]) -> None:
        mouse_x, mouse_y = position

        if not self._is_inside_world(mouse_x, mouse_y):
            self.selected_ant = None
            return

        closest_ant: Ant | None = None
        closest_distance = settings.CLICK_RADIUS

        for ant in self.ants:
            distance = ant.distance_to_position(
                mouse_x,
                mouse_y,
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
            f"entities={len(self._entities)}, "
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}"
            f")"
        )