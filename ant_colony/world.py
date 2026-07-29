import random as _random_module
from collections.abc import Iterator
from typing import TypeVar

from ant_colony.components import (
    AntState,
    FoodTargetSource,
    ResourceType,
)
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
from ant_colony.knowledge import EntityObservation

EntityType = TypeVar(
    "EntityType",
    bound=Entity,
)


class World:
    def __init__(
        self,
        rng: _random_module.Random | None = None,
    ) -> None:
        self._entities: list[Entity] = []
        self.selected_ant: Ant | None = None
        self._next_pheromone_id = 1
        self._next_food_id = 1
        self._next_ant_id = settings.STARTING_ANTS
        self._update_count = 0
        self._colony_complete = False
        self._rng = rng if rng is not None else _random_module.Random()

        self.add_entity(
            Nest(
                x=settings.NEST_POSITION[0],
                y=settings.NEST_POSITION[1],
            )
        )

        nest = self.nest
        for ant_id in range(
            settings.STARTING_ANTS
        ):
            ant = Ant(ant_id, rng=self._rng)
            ant.x = nest.x
            ant.y = nest.y
            self.add_entity(ant)

        for _ in range(settings.STARTING_FOOD_SOURCES):
            self.add_entity(self._spawn_food())

        self.add_entity(
            Water(
                water_id=1,
                x=settings.WATER_POSITION[0],
                y=settings.WATER_POSITION[1],
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

    @property
    def is_complete(self) -> bool:
        """True once the colony has reached ``MAX_ANTS`` for the first time."""
        return self._colony_complete

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
        if self._colony_complete:
            return

        for ant in self.ants:
            discovered_entities = self.sense_for(ant)

            self._assign_food_target(
                ant,
                discovered_entities,
            )

            self._assign_nest_target(ant)
            self._assign_water_target(ant, discovered_entities)

        for entity in tuple(self._entities):
            if not isinstance(entity, Ant):
                entity.update()

        for ant in self.ants:
            self._update_ant_movement(ant)

        just_deposited: list[Ant] = []
        for ant in self.ants:
            self._collect_food_for(ant)
            self._assign_nest_target(ant)
            deposited_nutrition = self._deposit_food_for(ant)
            if deposited_nutrition > 0:
                just_deposited.append(ant)
            self._drink_water_for(ant)

        self._deposit_pheromones()
        self._process_upkeep()

        # Process post-deposit return-trip selection in ascending ID order to
        # keep the behaviour deterministic regardless of deposit order.
        for ant in sorted(just_deposited, key=lambda a: a.id):
            self._assign_water_target(ant, ())
            if ant.state == AntState.WANDERING:
                self._assign_food_target(ant, ())

        self._maybe_spawn_ant()
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

        if not ant.inventory.is_empty:
            return

        target, source = self._find_food_target(ant, discovered_entities)

        if target is None:
            return

        # If the ant is leaving the nest for the first time (or again
        # after returning), charge the one-time excursion energy cost.
        if not ant.on_excursion and not ant.depart():
            # Insufficient energy — keep the ant at the nest.
            return

        ant.select_food_target(target, source=source)

    def _find_food_target(
        self,
        ant: Ant,
        discovered_entities: tuple[Entity, ...],
    ) -> tuple[Food | None, FoodTargetSource]:
        """Return the best food target and its source without side-effects."""
        discovered_food = tuple(
            entity
            for entity in discovered_entities
            if isinstance(entity, Food)
            and not entity.is_depleted
        )

        if discovered_food:
            closest_food = min(
                discovered_food,
                key=lambda food: (
                    ant.distance_to(food),
                    food.id,
                ),
            )
            return closest_food, FoodTargetSource.DISCOVERY

        pheromone_food = self._food_from_pheromones(
            ant,
            discovered_entities,
        )

        if pheromone_food is not None:
            return pheromone_food, FoodTargetSource.PHEROMONE

        remembered_food = self._remembered_food_for(ant)

        if remembered_food is not None:
            return remembered_food, FoodTargetSource.MEMORY

        return None, FoodTargetSource.DISCOVERY

    def _food_from_pheromones(
        self,
        ant: Ant,
        discovered_entities: tuple[Entity, ...],
    ) -> Food | None:
        food_by_id = {
            food.id: food
            for food in self.food
            if not food.is_depleted
        }
        recruitable: list[tuple[Pheromone, Food]] = []

        for entity in discovered_entities:
            if not isinstance(entity, Pheromone):
                continue

            source_food = food_by_id.get(entity.source_food_id)

            if source_food is None:
                continue

            recruitable.append((entity, source_food))

        if not recruitable:
            return None

        selected_pair = max(
            recruitable,
            key=lambda item: (
                item[0].strength,
                -item[0].id,
            ),
        )
        return selected_pair[1]

    def _remembered_food_for(
        self,
        ant: Ant,
    ) -> Food | None:
        food_by_id = {
            food.id: food
            for food in self.food
            if not food.is_depleted
        }
        remembered_food: list[Food] = []

        for memory in ant.knowledge.memories:
            observation = memory.value

            if not isinstance(observation, EntityObservation):
                continue

            if observation.entity_type != "food":
                continue

            food = food_by_id.get(observation.entity_id)

            if food is None:
                ant.knowledge.forget(memory.name)
                continue

            remembered_food.append(food)

        if not remembered_food:
            return None

        return min(
            remembered_food,
            key=lambda food: (
                ant.distance_to(food),
                food.id,
            ),
        )

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

    def _assign_water_target(
        self,
        ant: Ant,
        discovered_entities: tuple[Entity, ...],
    ) -> None:
        """Route a thirsty ant to the nearest available water source.

        Priority rule: an ant carrying food must deliver it first.  Only
        WANDERING or SEEKING_FOOD ants that are thirsty are redirected.
        """
        if not ant.is_thirsty:
            return

        # Food delivery takes priority over drinking.
        if ant.state == AntState.CARRYING_FOOD:
            return

        if ant.state == AntState.SEEKING_WATER:
            return

        available_water = tuple(
            water
            for water in self.water
            if not water.is_depleted
        )
        if not available_water:
            return

        # Prefer discovered water; fall back to all world water.
        discovered_water = tuple(
            entity
            for entity in discovered_entities
            if isinstance(entity, Water)
            and not entity.is_depleted
        )
        candidates = discovered_water if discovered_water else available_water

        target = min(
            candidates,
            key=lambda water: (
                ant.distance_to(water),
                water.id,
            ),
        )

        # Cancel any current food target before switching.
        if ant.food_target is not None:
            ant.clear_food_target()

        ant.select_water_target(target)

    def _drink_water_for(
        self,
        ant: Ant,
    ) -> bool:
        if ant.water_target is None:
            return False

        return ant.drink_from(ant.water_target)

    def _deposit_food_for(
        self,
        ant: Ant,
    ) -> int:
        if ant.nest_target is None:
            return 0

        deposited = ant.deposit_into(self.nest)
        if deposited > 0:
            ant.arrive()
        return deposited
    
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

            carried_food_portion = next(
                (
                    portion
                    for portion in ant.inventory.items
                    if portion.resource_type == ResourceType.FOOD
                    and isinstance(portion.source_id, int)
                ),
                None,
            )

            if carried_food_portion is None:
                continue

            self.add_entity(
                Pheromone(
                    pheromone_id=self._next_pheromone_id,
                    source_food_id=carried_food_portion.source_id,
                    x=ant.x,
                    y=ant.y,
                )
            )

            self._next_pheromone_id += 1

    def _update_ant_movement(self, ant: Ant) -> None:
        """Move an ant for one tick, gating wandering departure on nest proximity.

        A wandering ant that is physically at the nest must pay the one-time
        excursion cost before it can leave.  If it cannot afford to depart,
        only hydration decay runs and movement is suppressed this tick.
        """
        nest = self.nest
        at_nest = ant.intersects_entity(
            nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        )

        if (
            at_nest
            and not ant.on_excursion
            and ant.state in (
                AntState.WANDERING,
                AntState.SEEKING_FOOD,
                AntState.SEEKING_WATER,
            )
        ):
            if not ant.depart():
                # Insufficient energy — decay hydration only, no movement.
                ant.hydration.decay(settings.ANT_HYDRATION_DECAY_PER_UPDATE)
                return

        ant.update()

    def _process_upkeep(self) -> None:
        """Refuel ants physically at the nest in ascending ID order.

        An ant must be (a) spatially within the nest interaction boundary and
        (b) not currently on an excursion to be eligible for refuelling.
        Each 10-energy increment costs 1 nutrition from the nest reserve.
        Colony upkeep has priority over spawning.
        """
        nest = self.nest
        for ant in sorted(self.ants, key=lambda a: a.id):
            if ant.on_excursion:
                continue
            if not ant.intersects_entity(
                nest,
                padding=settings.ANT_INTERACTION_RADIUS,
            ):
                continue
            while not ant.energy.is_full:
                if not nest.consume(settings.ANT_REFUEL_FOOD_COST):
                    break
                ant.energy.restore(settings.ANT_REFUEL_ENERGY_AMOUNT)

    def _maybe_spawn_ant(self) -> None:
        if len(self.ants) >= settings.MAX_ANTS:
            return

        nest = self.nest
        if not nest.consume(settings.ANT_SPAWN_FOOD_COST):
            return

        new_ant = Ant(self._next_ant_id, rng=self._rng)
        self._next_ant_id += 1
        new_ant.x = nest.x
        new_ant.y = nest.y
        self.add_entity(new_ant)

        if len(self.ants) >= settings.MAX_ANTS:
            self._colony_complete = True

    def _spawn_food(self) -> Food:
        food_id = self._next_food_id
        self._next_food_id += 1

        x = self._rng.uniform(
            settings.FOOD_RADIUS,
            settings.WORLD_WIDTH - settings.FOOD_RADIUS,
        )
        y = self._rng.uniform(
            settings.FOOD_RADIUS,
            settings.WORLD_HEIGHT - settings.FOOD_RADIUS,
        )

        return Food(
            food_id=food_id,
            x=x,
            y=y,
            nutrition=5,
            quantity=10,
        )

    def _remove_depleted_pheromones(self) -> None:
        for pheromone in self.pheromones:
            if pheromone.is_depleted:
                self.remove_entity(pheromone)

    def _remove_depleted_resources(self) -> None:
        for resource in self.resources:
            if resource.is_depleted:
                self.remove_entity(resource)
                # After removing the depleted source, replace it only if
                # the active count is still below the cap.  len(self.food)
                # is evaluated post-removal so the check is intentionally
                # against the already-reduced count.
                if isinstance(resource, Food):
                    if len(self.food) < settings.STARTING_FOOD_SOURCES:
                        self.add_entity(self._spawn_food())

    def _clear_resource_target_references(
        self,
        resource: Resource,
    ) -> None:
        if not isinstance(resource, Food):
            return

        memory_name = EntityObservation.from_entity(
            resource
        ).memory_name

        for ant in self.ants:
            ant.knowledge.forget(memory_name)

            if ant.food_target is resource:
                ant.clear_food_target()

        for pheromone in self.pheromones:
            if pheromone.source_food_id == resource.id:
                self.remove_entity(pheromone)

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

    def entity_under_position(
        self,
        position: tuple[float, float],
    ) -> Entity | None:
        x, y = position

        if not self._is_inside_world(x, y):
            return None

        matching_entities = tuple(
            entity
            for entity in self._entities
            if entity.intersects_position(x, y)
        )

        if not matching_entities:
            return None

        return min(
            matching_entities,
            key=lambda entity: entity.distance_to_position(
                x,
                y,
            ),
        )

    @staticmethod
    def _is_inside_world(
        x: float,
        y: float,
    ) -> bool:
        return (
            0 <= x <= settings.WORLD_WIDTH
            and 0 <= y <= settings.WORLD_HEIGHT
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
