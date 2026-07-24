from collections.abc import Iterator
from typing import TypeVar

from ant_colony.components import AntState
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.building_material import (
    BuildingMaterial,
)
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.entities.pheromone import Pheromone
from ant_colony.entities.resource import Resource
from ant_colony.entities.water import Water

EntityType = TypeVar(
    "EntityType",
    bound=Entity,
)


class World:
    def __init__(self) -> None:
        self._entities: list[Entity] = []
        self.selected_ant: Ant | None = None
        self._next_pheromone_id = 1
        self._update_count = 0

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

        self.add_entity(
            Water(
                water_id=1,
                x=750,
                y=180,
                hydration=4,
                quantity=15,
            )
        )

        self.add_entity(
            BuildingMaterial(
                material_id=1,
                x=700,
                y=520,
                construction_value=3,
                quantity=12,
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
    def water(self) -> tuple[Water, ...]:
        return self.entities_of_type(Water)

    @property
    def building_materials(
        self,
    ) -> tuple[BuildingMaterial, ...]:
        return self.entities_of_type(BuildingMaterial)

    @property
    def resources(self) -> tuple[Resource, ...]:
        return self.entities_of_type(Resource)
    
    @property
    def pheromones(self) -> tuple[Pheromone, ...]:
        return self.entities_of_type(Pheromone)

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

        if isinstance(entity, Resource):
            self._clear_resource_target_references(entity)

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
            discovered_entities = self.sense_for(ant)

            self._assign_food_target(
                ant,
                discovered_entities,
            )

            self._assign_nest_target(ant)

        for entity in tuple(self._entities):
            entity.update()

        for ant in self.ants:
            self._collect_food_for(ant)
            self._assign_nest_target(ant)
            self._deposit_food_for(ant)

        self._deposit_pheromones()
        self._remove_depleted_resources()
        self._remove_depleted_pheromones()
        self._update_count += 1

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

    def _assign_nest_target(
        self,
        ant: Ant,
    ) -> None:
        if ant.state != AntState.CARRYING_FOOD:
            return

        if ant.inventory.is_empty:
            return

        if ant.nest_target is not None:
            return

        ant.select_nest_target(self.nest)

    def _deposit_food_for(
        self,
        ant: Ant,
    ) -> None:
        if ant.nest_target is None:
            return

        ant.deposit_into(self.nest)
    
    def _collect_food_for(
        self,
        ant: Ant,
    ) -> None:
        target = ant.food_target

        if target is None:
            return

        ant.collect_from(target)

    def _deposit_pheromones(self) -> None:
        if self._update_count % settings.PHEROMONE_DEPOSIT_INTERVAL != 0:
            return

        for ant in self.ants:
            if ant.state != AntState.CARRYING_FOOD:
                continue

            if ant.inventory.is_empty:
                continue

            self.add_entity(
                Pheromone(
                    pheromone_id=self._next_pheromone_id,
                    x=ant.x,
                    y=ant.y,
                )
            )

            self._next_pheromone_id += 1

    def _remove_depleted_pheromones(self) -> None:
        for pheromone in self.pheromones:
            if pheromone.is_depleted:
                self.remove_entity(pheromone)

    def _remove_depleted_resources(self) -> None:
        for resource in self.resources:
            if resource.is_depleted:
                self.remove_entity(resource)

    def _clear_resource_target_references(
        self,
        resource: Resource,
    ) -> None:
        if not isinstance(resource, Food):
            return

        for ant in self.ants:
            if ant.food_target is resource:
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
            f"food={len(self.food)}, "
            f"water={len(self.water)}, "
            f"building_materials="
            f"{len(self.building_materials)}, "
            f"pheromones={len(self.pheromones)}"
            f")"
        )