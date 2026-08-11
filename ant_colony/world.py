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
from ant_colony.entities.entity import Entity
from ant_colony.entities.food import Food
from ant_colony.entities.nest import Nest
from ant_colony.entities.pheromone import Pheromone, PheromoneType
from ant_colony.entities.resource import Resource
from ant_colony.geometry import RectangleObstacle
from ant_colony.knowledge import EntityObservation
from ant_colony.scenarios import (
    DEFAULT_SCENARIO,
    Scenario,
    get_scenario,
)
from ant_colony.systems.collision import CollisionMap
from ant_colony.systems.navigation import AntNavigator

EntityType = TypeVar(
    "EntityType",
    bound=Entity,
)


class World:
    def __init__(
        self,
        rng: _random_module.Random | None = None,
        scenario: Scenario | str | None = None,
    ) -> None:
        if scenario is None:
            self._scenario = DEFAULT_SCENARIO
        elif isinstance(scenario, str):
            self._scenario = get_scenario(scenario)
        else:
            self._scenario = scenario

        self._entities: list[Entity] = []
        self.selected_ant: Ant | None = None
        self._active_route_blockers: tuple[RectangleObstacle, ...] = ()
        self._route_blocker_trip_count = 0
        self._next_pheromone_id = 1
        self._next_food_id = 1
        self._next_ant_id = settings.STARTING_ANTS
        self._update_count = 0
        self._colony_complete = False
        self._rng = rng if rng is not None else _random_module.Random()
        self._collision_map = CollisionMap(lambda: self.obstacles)
        self._navigator = AntNavigator(self, self._collision_map)
        self._blocked_headings = self._navigator._blocked_headings
        self._wall_follow_sides = self._navigator._wall_follow_sides
        self._wall_follow_progress = self._navigator._wall_follow_progress

        nest_x, nest_y = self._scenario.nest_position
        self._require_spawn_position_available(
            nest_x,
            nest_y,
            radius=settings.NEST_RADIUS,
            label="nest",
        )
        self.add_entity(Nest(x=nest_x, y=nest_y))

        nest = self.nest
        for ant_id in range(
            settings.STARTING_ANTS
        ):
            ant = Ant(ant_id, rng=self._rng)
            ant.x = nest.x
            ant.y = nest.y
            self._require_spawn_position_available(
                ant.x,
                ant.y,
                radius=ant.hitbox_radius,
                label="initial ant",
            )
            self.add_entity(ant)

        for source_index in range(
            settings.STARTING_FOOD_SOURCES
        ):
            self.add_entity(
                self._spawn_initial_food(source_index)
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
    def resources(self) -> tuple[Resource, ...]:
        return self.entities_of_type(Resource)

    @property
    def pheromones(self) -> tuple[Pheromone, ...]:
        return self.entities_of_type(Pheromone)

    @property
    def obstacles(self) -> tuple[RectangleObstacle, ...]:
        return self._scenario.obstacles + self._active_route_blockers

    @property
    def route_blockers(self) -> tuple[RectangleObstacle, ...]:
        return self._scenario.route_blockers

    @property
    def route_blockers_active(self) -> bool:
        return bool(self._active_route_blockers)

    @property
    def route_blocker_trip_count(self) -> int:
        return self._route_blocker_trip_count

    @property
    def scenario_name(self) -> str:
        return self._scenario.name

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

    @property
    def max_ants(self) -> int:
        return self._scenario.max_ants or settings.MAX_ANTS

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
            self._visible_entities_for(
                ant,
                ant.senses.detect(
                    observer=ant,
                    candidates=self.entities,
                ),
            )
        )

        for entity in discovered_entities:
            ant.observe(entity)
            if isinstance(entity, Food):
                entity.mark_discovered()

        return discovered_entities

    def _visible_entities_for(
        self,
        observer: Ant,
        candidates: tuple[Entity, ...],
    ) -> tuple[Entity, ...]:
        return tuple(
            candidate
            for candidate in candidates
            if not self._entity_is_occluded(observer, candidate)
        )

    def _entity_is_occluded(
        self,
        observer: Ant,
        target: Entity,
    ) -> bool:
        if not isinstance(target, Food):
            return False

        return self._movement_intersects_obstacle(
            (observer.x, observer.y),
            (target.x, target.y),
        )

    def update(self) -> None:
        if self._colony_complete:
            return

        self._update_route_blockers()

        for ant in self.ants:
            discovered_entities = self.sense_for(ant)

            self._assign_food_target(
                ant,
                discovered_entities,
            )

            self._assign_nest_target(ant)

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

        self._deposit_pheromones()
        self._process_upkeep()

        # Process post-deposit return-trip selection in ascending ID order to
        # keep the behaviour deterministic regardless of deposit order.
        for ant in sorted(just_deposited, key=lambda a: a.id):
            self._assign_food_target(ant, ())

        self._maybe_spawn_ant()
        self._remove_depleted_resources()
        self._remove_depleted_pheromones()
        self._update_count += 1

    def _update_route_blockers(self) -> None:
        if self._active_route_blockers:
            return

        activation_tick = self._scenario.route_blocker_activation_tick
        if activation_tick is None:
            return

        if self._update_count >= activation_tick:
            self._activate_route_blockers()

    def _activate_route_blockers(self) -> None:
        self._active_route_blockers = self._scenario.route_blockers

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

            if entity.pheromone_type != PheromoneType.FOOD:
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

        if ant.collect_from(target):
            self._record_route_blocker_trip_if_needed(ant)

    def _record_route_blocker_trip_if_needed(
        self,
        ant: Ant,
    ) -> None:
        activation_trip_count = (
            self._scenario.route_blocker_activation_trip_count
        )

        if activation_trip_count is None:
            return

        if self._active_route_blockers:
            return

        if not self._return_leg_crosses_route_blocker(ant):
            return

        self._route_blocker_trip_count += 1

        if self._route_blocker_trip_count >= activation_trip_count:
            self._activate_route_blockers()

    def _return_leg_crosses_route_blocker(
        self,
        ant: Ant,
    ) -> bool:
        return any(
            blocker.intersects_segment(
                (ant.x, ant.y),
                (self.nest.x, self.nest.y),
            )
            for blocker in self._scenario.route_blockers
        )

    def _deposit_pheromones(self) -> None:
        if self._update_count % settings.PHEROMONE_DEPOSIT_INTERVAL != 0:
            return

        for ant in self.ants:
            self._deposit_pheromone_for_ant(ant)

    def _deposit_pheromone_for_ant(
        self,
        ant: Ant,
    ) -> None:
        pheromone_type = self._pheromone_type_for(ant)
        source_food_id = self._pheromone_source_food_id_for(ant)

        if pheromone_type == PheromoneType.FOOD and source_food_id is None:
            return

        self.add_entity(
            Pheromone(
                pheromone_id=self._next_pheromone_id,
                source_food_id=source_food_id,
                pheromone_type=pheromone_type,
                x=ant.x,
                y=ant.y,
            )
        )
        self._next_pheromone_id += 1

    @staticmethod
    def _pheromone_type_for(
        ant: Ant,
    ) -> PheromoneType:
        if ant.state in (AntState.SEEKING_FOOD, AntState.CARRYING_FOOD):
            return PheromoneType.FOOD
        return PheromoneType.EXPLORE

    @staticmethod
    def _pheromone_source_food_id_for(
        ant: Ant,
    ) -> int | None:
        if ant.state == AntState.SEEKING_FOOD and ant.food_target is not None:
            return ant.food_target.id

        if ant.state != AntState.CARRYING_FOOD:
            return None

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
            return None

        return carried_food_portion.source_id

    def _update_ant_movement(self, ant: Ant) -> None:
        self._navigator.update_ant_movement(ant)

    def _move_ant_around_obstacle(
        self,
        ant: Ant,
        blocked_count: int = 1,
    ) -> None:
        self._navigator.move_ant_around_obstacle(ant, blocked_count)

    def _record_blocked_heading(
        self,
        ant: Ant,
        heading: float,
    ) -> int:
        return self._navigator.record_blocked_heading(ant, heading)

    def _deposit_avoid_pheromone_for(self, ant: Ant) -> None:
        self._navigator._deposit_avoid_pheromone_for(ant)

    def _target_distance_for(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> float:
        return self._navigator.target_distance_for(ant, candidate)

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
        if len(self.ants) >= self.max_ants:
            return

        nest = self.nest
        if not nest.consume(settings.ANT_SPAWN_FOOD_COST):
            return

        new_ant = Ant(self._next_ant_id, rng=self._rng)
        self._next_ant_id += 1
        new_ant.x = nest.x
        new_ant.y = nest.y
        self._require_spawn_position_available(
            new_ant.x,
            new_ant.y,
            radius=new_ant.hitbox_radius,
            label="spawned ant",
        )
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
        attempts = 0
        while self._position_is_blocked(
            x,
            y,
            radius=settings.FOOD_RADIUS,
        ):
            attempts += 1
            if attempts > settings.FOOD_SPAWN_MAX_ATTEMPTS:
                raise RuntimeError(
                    "Unable to place food in unblocked space."
                )
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
            nutrition=settings.FOOD_NUTRITION,
            quantity=settings.FOOD_QUANTITY,
        )

    def _spawn_initial_food(
        self,
        source_index: int,
    ) -> Food:
        if source_index < len(self._scenario.initial_food_positions):
            x, y = self._scenario.initial_food_positions[source_index]
            bounded_x = min(
                max(x, settings.FOOD_RADIUS),
                settings.WORLD_WIDTH
                - settings.FOOD_RADIUS,
            )
            bounded_y = min(
                max(y, settings.FOOD_RADIUS),
                settings.WORLD_HEIGHT
                - settings.FOOD_RADIUS,
            )
            food_id = self._next_food_id
            self._next_food_id += 1
            if self._position_is_blocked(
                bounded_x,
                bounded_y,
                radius=settings.FOOD_RADIUS,
            ):
                return self._spawn_food()
            return Food(
                food_id=food_id,
                x=bounded_x,
                y=bounded_y,
                nutrition=settings.FOOD_NUTRITION,
                quantity=settings.FOOD_QUANTITY,
            )
        return self._spawn_food()

    def _movement_intersects_obstacle(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        radius: float = 0.0,
    ) -> bool:
        return self._collision_map.movement_intersects_obstacle(
            start,
            end,
            radius=radius,
        )

    def _position_is_blocked(
        self,
        x: float,
        y: float,
        *,
        radius: float = 0.0,
    ) -> bool:
        return self._collision_map.position_is_blocked(
            x,
            y,
            radius=radius,
        )

    def _require_spawn_position_available(
        self,
        x: float,
        y: float,
        *,
        radius: float,
        label: str,
    ) -> None:
        if self._position_is_blocked(
            x,
            y,
            radius=radius,
        ):
            raise ValueError(
                f"Cannot place {label} at blocked position ({x}, {y})."
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
            and 0
            <= y
            <= settings.WORLD_HEIGHT
        )

    def __repr__(self) -> str:
        return (
            f"World("
            f"entities={len(self._entities)}, "
            f"ants={len(self.ants)}, "
            f"food={len(self.food)}, "
            f"pheromones={len(self.pheromones)}"
            f")"
        )
