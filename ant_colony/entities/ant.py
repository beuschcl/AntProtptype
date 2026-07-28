from __future__ import annotations

import math
import random as _random_module
from typing import TYPE_CHECKING

from ant_colony.components import (
    AntState,
    EnergyNeed,
    FoodTargetSource,
    HydrationNeed,
    Inventory,
    Senses,
)
from ant_colony.config import settings
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Polygon, Shape
from ant_colony.knowledge import (
    EntityObservation,
    Knowledge,
)

if TYPE_CHECKING:
    from ant_colony.entities.food import Food
    from ant_colony.entities.nest import Nest
    from ant_colony.entities.water import Water


class Ant(Entity):
    def __init__(
        self,
        ant_id: int,
        rng: _random_module.Random | None = None,
    ) -> None:
        self._rng = rng if rng is not None else _random_module.Random()
        x = self._rng.uniform(
            settings.ANT_BOUNDARY_PADDING,
            settings.WORLD_WIDTH - settings.ANT_BOUNDARY_PADDING,
        )
        y = self._rng.uniform(
            settings.ANT_BOUNDARY_PADDING,
            settings.WORLD_HEIGHT - settings.ANT_BOUNDARY_PADDING,
        )

        super().__init__(
            entity_id=ant_id,
            x=x,
            y=y,
            discoverable_radius=(settings.ANT_DISCOVERABLE_RADIUS),
        )

        self.speed = self._rng.uniform(
            settings.ANT_MIN_SPEED,
            settings.ANT_MAX_SPEED,
        )
        self.heading = self._rng.uniform(
            0,
            360,
        )

        self.state = AntState.WANDERING
        self.senses = Senses()
        self.inventory = Inventory(capacity=settings.ANT_INVENTORY_CAPACITY)
        self.knowledge = Knowledge()
        self.hydration = HydrationNeed(
            maximum=settings.ANT_MAX_HYDRATION,
        )
        self.energy = EnergyNeed(maximum=settings.ANT_MAX_ENERGY)

        self._on_excursion: bool = False
        self._food_target: Food | None = None
        self._food_target_source: FoodTargetSource | None = None
        self._nest_target: Nest | None = None
        self._water_target: Water | None = None

    @property
    def food_target(self) -> Food | None:
        return self._food_target

    @property
    def food_target_source(self) -> FoodTargetSource | None:
        return self._food_target_source

    @property
    def nest_target(self) -> Nest | None:
        return self._nest_target

    @property
    def water_target(self) -> Water | None:
        return self._water_target

    @property
    def is_thirsty(self) -> bool:
        """True when hydration is at or below the thirst threshold."""
        return self.hydration.current <= settings.ANT_THIRST_THRESHOLD

    @property
    def on_excursion(self) -> bool:
        """True while the ant is away from the nest on a field trip."""
        return self._on_excursion

    def depart(self) -> bool:
        """Charge excursion energy and mark the ant as departed.

        Returns ``True`` if the ant had enough energy and the departure
        was recorded.  Returns ``False`` (no-op) if energy is
        insufficient.
        """
        if self.energy.spend(settings.ANT_EXCURSION_ENERGY_COST):
            self._on_excursion = True
            return True
        return False

    def arrive(self) -> None:
        """Mark the ant as returned to the nest."""
        self._on_excursion = False

    @property
    def hitbox_radius(self) -> float:
        return settings.ANT_RADIUS

    def update(self) -> None:
        self.hydration.decay(settings.ANT_HYDRATION_DECAY_PER_UPDATE)
        if self.state == AntState.WANDERING:
            if self.hydration.current > 0:
                self.wander()
        elif self.state == AntState.SEEKING_FOOD:
            self.move_toward_food()
        elif self.state == AntState.CARRYING_FOOD:
            self.move_toward_nest()
        elif self.state == AntState.SEEKING_WATER:
            self.move_toward_water()

    def observe(
        self,
        entity: Entity,
    ) -> EntityObservation:
        observation = EntityObservation.from_entity(entity)

        self.knowledge.remember(
            observation.memory_name,
            observation,
        )

        return observation

    def select_food_target(
        self,
        food: Food,
        source: FoodTargetSource = FoodTargetSource.DISCOVERY,
    ) -> bool:
        if self.inventory.count() > 0:
            return False

        if food.is_depleted:
            return False

        self._nest_target = None
        self._food_target = food
        self._food_target_source = source
        self.state = AntState.SEEKING_FOOD
        return True

    def clear_food_target(self) -> None:
        self._food_target = None
        self._food_target_source = None

        if self.inventory.is_empty:
            self.state = AntState.WANDERING
        else:
            self.state = AntState.CARRYING_FOOD

    def select_nest_target(
        self,
        nest: Nest,
    ) -> bool:
        if self.inventory.is_empty:
            return False

        self._food_target = None
        self._nest_target = nest
        self.state = AntState.CARRYING_FOOD
        return True

    def clear_nest_target(self) -> None:
        self._nest_target = None

        if self.inventory.is_empty:
            self.state = AntState.WANDERING
        else:
            self.state = AntState.CARRYING_FOOD

    def select_water_target(
        self,
        water: Water,
    ) -> bool:
        self._food_target = None
        self._food_target_source = None
        self._nest_target = None
        self._water_target = water
        self.state = AntState.SEEKING_WATER
        return True

    def clear_water_target(self) -> None:
        self._water_target = None
        self.state = AntState.WANDERING

    def can_drink(
        self,
        water: Water,
    ) -> bool:
        return not water.is_depleted and self.intersects_entity(
            water,
            padding=settings.ANT_INTERACTION_RADIUS,
        )

    def drink_from(
        self,
        water: Water,
    ) -> bool:
        if not self.can_drink(water):
            return False

        self.hydration.restore(self.hydration.maximum - self.hydration.current)
        self.arrive()
        self.clear_water_target()
        return True

    def can_collect(
        self,
        food: Food,
    ) -> bool:
        return (
            not self.inventory.is_full
            and not food.is_depleted
            and self.intersects_entity(
                food,
                padding=settings.ANT_INTERACTION_RADIUS,
            )
        )

    def collect_from(
        self,
        food: Food,
    ) -> bool:
        if not self.can_collect(food):
            return False

        portion = food.collect()

        if portion is None:
            return False

        if not self.inventory.add(portion):
            raise RuntimeError(
                "Food was collected but could not be stored in the ant inventory."
            )

        self.clear_food_target()
        return True

    def can_deposit(
        self,
        nest: Nest,
    ) -> bool:
        return not self.inventory.is_empty and self.intersects_entity(
            nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        )

    def deposit_into(
        self,
        nest: Nest,
    ) -> int:
        if not self.can_deposit(nest):
            return 0

        portions = self.inventory.clear()
        deposited_nutrition = nest.deposit(portions)

        self.clear_nest_target()
        return deposited_nutrition

    def move_toward_food(self) -> None:
        if self._food_target is None or self._food_target.is_depleted:
            self.clear_food_target()
            return

        self.move_toward(
            self._food_target.x,
            self._food_target.y,
        )

    def move_toward_nest(self) -> None:
        if self._nest_target is None:
            return

        self.move_toward(
            self._nest_target.x,
            self._nest_target.y,
        )

    def move_toward_water(self) -> None:
        if self._water_target is None:
            return

        self.move_toward(
            self._water_target.x,
            self._water_target.y,
        )

    def move_toward(
        self,
        x: float,
        y: float,
    ) -> None:
        x_distance = x - self.x
        y_distance = y - self.y
        distance = math.hypot(
            x_distance,
            y_distance,
        )

        if distance == 0:
            return

        movement_distance = min(
            self.speed,
            distance,
        )

        self.x += x_distance / distance * movement_distance
        self.y += y_distance / distance * movement_distance

        self.heading = math.degrees(
            math.atan2(
                y_distance,
                x_distance,
            )
        )

        self.contain_position()

    def wander(self) -> None:
        heading_radians = math.radians(self.heading)

        self.x += math.cos(heading_radians) * self.speed
        self.y += math.sin(heading_radians) * self.speed

        self.heading += self._rng.uniform(
            -settings.ANT_TURN_SPEED,
            settings.ANT_TURN_SPEED,
        )

        self.contain_position()

    def contain_position(self) -> None:
        padding = settings.ANT_BOUNDARY_PADDING
        hit_horizontal_boundary = not (
            padding <= self.x <= settings.WORLD_WIDTH - padding
        )
        hit_vertical_boundary = not (
            padding <= self.y <= settings.WORLD_HEIGHT - padding
        )

        self.x = min(
            max(self.x, padding),
            settings.WORLD_WIDTH - padding,
        )
        self.y = min(
            max(self.y, padding),
            settings.WORLD_HEIGHT - padding,
        )

        if hit_horizontal_boundary:
            self.heading = 180 - self.heading
        if hit_vertical_boundary:
            self.heading = -self.heading
        self.heading %= 360

    def wrap_position(self) -> None:
        """Compatibility alias for the former wrapping boundary."""
        self.contain_position()

    def shapes(self) -> tuple[Shape, ...]:
        heading_radians = math.radians(self.heading)

        front = (
            self.x + math.cos(heading_radians) * settings.ANT_DRAW_LENGTH,
            self.y + math.sin(heading_radians) * settings.ANT_DRAW_LENGTH,
        )

        left = (
            self.x + math.cos(heading_radians + 2.5) * settings.ANT_DRAW_WIDTH,
            self.y + math.sin(heading_radians + 2.5) * settings.ANT_DRAW_WIDTH,
        )

        right = (
            self.x + math.cos(heading_radians - 2.5) * settings.ANT_DRAW_WIDTH,
            self.y + math.sin(heading_radians - 2.5) * settings.ANT_DRAW_WIDTH,
        )

        return (
            Polygon(
                points=(
                    front,
                    left,
                    right,
                ),
                color=settings.ANT_COLOR,
            ),
        )
