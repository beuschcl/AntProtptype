from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from ant_colony.components import (
    AntState,
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


class Ant(Entity):
    def __init__(self, ant_id: int) -> None:
        x = random.uniform(
            settings.ANT_BOUNDARY_PADDING,
            settings.WORLD_WIDTH - settings.ANT_BOUNDARY_PADDING,
        )
        y = random.uniform(
            settings.ANT_BOUNDARY_PADDING,
            settings.WORLD_HEIGHT - settings.ANT_BOUNDARY_PADDING,
        )

        super().__init__(
            entity_id=ant_id,
            x=x,
            y=y,
            discoverable_radius=(
                settings.ANT_DISCOVERABLE_RADIUS
            ),
        )

        self.speed = random.uniform(
            settings.ANT_MIN_SPEED,
            settings.ANT_MAX_SPEED,
        )
        self.heading = random.uniform(
            0,
            360,
        )

        self.state = AntState.WANDERING
        self.senses = Senses()
        self.inventory = Inventory(
            capacity=settings.ANT_INVENTORY_CAPACITY
        )
        self.knowledge = Knowledge()

        self._food_target: Food | None = None
        self._nest_target: Nest | None = None

    @property
    def food_target(self) -> Food | None:
        return self._food_target

    @property
    def nest_target(self) -> Nest | None:
        return self._nest_target

    @property
    def hitbox_radius(self) -> float:
        return settings.ANT_RADIUS

    def update(self) -> None:
        if self.state == AntState.WANDERING:
            self.wander()
        elif self.state == AntState.SEEKING_FOOD:
            self.move_toward_food()
        elif self.state == AntState.CARRYING_FOOD:
            self.move_toward_nest()

    def observe(
        self,
        entity: Entity,
    ) -> EntityObservation:
        observation = EntityObservation.from_entity(
            entity
        )

        self.knowledge.remember(
            observation.memory_name,
            observation,
        )

        return observation

    def select_food_target(
        self,
        food: Food,
    ) -> bool:
        if self.inventory.count() > 0:
            return False

        if food.is_depleted:
            return False


        self._nest_target = None
        self._food_target = food
        self.state = AntState.SEEKING_FOOD
        return True

    def clear_food_target(self) -> None:
        self._food_target = None

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
                "Food was collected but could not be "
                "stored in the ant inventory."
            )

        self.clear_food_target()
        return True

    def can_deposit(
        self,
        nest: Nest,
    ) -> bool:
        return (
            not self.inventory.is_empty
            and self.intersects_entity(
                nest,
                padding=settings.ANT_INTERACTION_RADIUS,
            )
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
        if (
            self._food_target is None
            or self._food_target.is_depleted
        ):
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

        self.x += (
            x_distance
            / distance
            * movement_distance
        )
        self.y += (
            y_distance
            / distance
            * movement_distance
        )

        self.heading = math.degrees(
            math.atan2(
                y_distance,
                x_distance,
            )
        )

        self.contain_position()

    def wander(self) -> None:
        heading_radians = math.radians(
            self.heading
        )

        self.x += (
            math.cos(heading_radians)
            * self.speed
        )
        self.y += (
            math.sin(heading_radians)
            * self.speed
        )

        self.heading += random.uniform(
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
        heading_radians = math.radians(
            self.heading
        )

        front = (
            self.x
            + math.cos(heading_radians)
            * settings.ANT_DRAW_LENGTH,
            self.y
            + math.sin(heading_radians)
            * settings.ANT_DRAW_LENGTH,
        )

        left = (
            self.x
            + math.cos(
                heading_radians + 2.5
            )
            * settings.ANT_DRAW_WIDTH,
            self.y
            + math.sin(
                heading_radians + 2.5
            )
            * settings.ANT_DRAW_WIDTH,
        )

        right = (
            self.x
            + math.cos(
                heading_radians - 2.5
            )
            * settings.ANT_DRAW_WIDTH,
            self.y
            + math.sin(
                heading_radians - 2.5
            )
            * settings.ANT_DRAW_WIDTH,
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
