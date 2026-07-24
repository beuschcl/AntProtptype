from collections.abc import Iterator
from typing import TypeVar

from ant_colony.components import AntState
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest

EntityType = TypeVar(
    "EntityType",
    bound=Entity,
)


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

        for ant_id in range(
            settings.STARTING_ANTS
        ):
            self.add_entity(
                Ant(ant_id)
            )

        self.add_entity(
            Food(
                food_id=1,
                x=200,
                y=200,
                nutrition=5,
                quantity=10,
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

    def add_entity(
        self,
        entity: Entity,
    ) -> None:
        if entity in self._entities:
            raise ValueError(
                "The entity is already registered "
                "with this world."
            )

        self._entities.append(entity)

    def remove_entity(
        self,
        entity: Entity,
    ) -> None:
        try:
            self._entities.remove(entity)
        except ValueError as error:
            raise ValueError(
                "The entity is not registered "
                "with this world."
            ) from error

        if entity is self.selected_ant:
            self.selected_ant = None

        if isinstance(entity, Food):
            self._clear_food_target_references(entity)

    def entities_of_type(
        self,
        entity_type: type[EntityType],
    ) -> tuple[EntityType, ...]:
        return tuple(
            entity
            for entity in self._entities
            if isinstance(
                entity,
                entity_type,
            )
        )

    def sense_for(
        self,
        ant: Ant,
    ) -> tuple[Entity, ...]:
        if ant not in self._entities:
            raise ValueError(
                "The ant is not registered "
                "with this world."
            )

        discovered_entities = (
            ant.senses.detect(
                observer=ant,
                candidates=self.entities,
            )
        )

        for entity in discovered_entities:
            ant.observe(entity)

        return discovered_entities

    def update(self) -> None:
        for ant in self.ants:
            discovered_entities = self.sense_for(
                ant
            )

            self._assign_food_target(
                ant,
                discovered_entities,
            )

        for entity in tuple(self._entities):
            entity.update()

        for ant in self.ants:
            self._collect_food_for(ant)

        self._remove_depleted_food()

    def _assign_food_target(
        self,
        ant: Ant,
        discovered_entities: tuple[Entity, ...],
    ) -> None:
        if ant.state != AntState.WANDERING:
            return

        discovered_food = tuple(
            entity
            for entity in discovered_entities
            if isinstance(entity, Food)
            and not entity.is_depleted
        )

        if not discovered_food:
            return

        closest_food = min(
            discovered_food,
            key=ant.distance_to,
        )

        ant.select_food_target(closest_food)

    def _collect_food_for(
        self,
        ant: Ant,
    ) -> None:
        target = ant.food_target

        if target is None:
            return

        ant.collect_from(target)

    def _remove_depleted_food(self) -> None:
        for food in self.food:
            if food.is_depleted:
                self.remove_entity(food)

    def _clear_food_target_references(
        self,
        food: Food,
    ) -> None:
        for ant in self.ants:
            if ant.food_target is food:
                ant.clear_food_target()

    def __iter__(self) -> Iterator[Entity]:
        return iter(self._entities)

    def handle_click(
        self,
        position: tuple[float, float],
    ) -> None:
        mouse_x, mouse_y = position

        if not self._is_inside_world(
            mouse_x,
            mouse_y,
        ):
            self.selected_ant = None
            return

        closest_ant: Ant | None = None
        closest_distance = (
            settings.CLICK_RADIUS
        )

        for ant in self.ants:
            distance = (
                ant.distance_to_position(
                    mouse_x,
                    mouse_y,
                )
            )

            if distance < closest_distance:
                closest_ant = ant
                closest_distance = distance

        self.selected_ant = closest_ant

    @staticmethod
    def _is_inside_world(
        x: float,
        y: float,
    ) -> bool:
        return (
            0 <= x <= settings.WORLD_WIDTH
            and 0
            <= y
            <= settings.SCREEN_HEIGHT
        )

    def __repr__(self) -> str:
        return (
            f"World("
            f"entities={len(self._entities)}, "
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}"
            f")"
        )