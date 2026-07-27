from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ant_colony.entities.ant import Ant
    from ant_colony.world import World


@dataclass(frozen=True, slots=True)
class InspectorSnapshot:
    ant_count: int
    food_source_count: int
    remaining_food_portions: int
    water_source_count: int
    building_material_source_count: int
    nest_food_reserve: int
    delivered_portions: int
    pheromone_count: int
    selected_ant_id: int | None = None
    selected_ant_x: float | None = None
    selected_ant_y: float | None = None
    selected_ant_speed: float | None = None
    selected_ant_heading: float | None = None
    selected_ant_state: str | None = None
    selected_ant_inventory_count: int | None = None
    selected_ant_inventory_capacity: int | None = None
    selected_ant_knowledge_count: int | None = None
    selected_ant_target: str | None = None

    @classmethod
    def from_world(
        cls,
        world: World,
    ) -> InspectorSnapshot:
        selected_ant = world.selected_ant

        if selected_ant is None:
            return cls(
                ant_count=len(world.ants),
                food_source_count=len(world.food),
                remaining_food_portions=sum(
                    food.quantity
                    for food in world.food
                ),
                water_source_count=len(world.water),
                building_material_source_count=(
                    len(world.building_materials)
                ),
                nest_food_reserve=world.nest.food_reserve,
                delivered_portions=world.nest.delivered_portions,
                pheromone_count=len(world.pheromones),
            )

        return cls._from_selected_ant(
            world,
            selected_ant,
        )

    @classmethod
    def _from_selected_ant(
        cls,
        world: World,
        ant: Ant,
    ) -> InspectorSnapshot:
        return cls(
            ant_count=len(world.ants),
            food_source_count=len(world.food),
            remaining_food_portions=sum(
                food.quantity
                for food in world.food
            ),
            water_source_count=len(world.water),
            building_material_source_count=(
                len(world.building_materials)
            ),
            nest_food_reserve=world.nest.food_reserve,
            delivered_portions=world.nest.delivered_portions,
            pheromone_count=len(world.pheromones),
            selected_ant_id=ant.id,
            selected_ant_x=ant.x,
            selected_ant_y=ant.y,
            selected_ant_speed=ant.speed,
            selected_ant_heading=ant.heading,
            selected_ant_state=ant.state.value,
            selected_ant_inventory_count=ant.inventory.count(),
            selected_ant_inventory_capacity=ant.inventory.capacity,
            selected_ant_knowledge_count=ant.knowledge.count(),
            selected_ant_target=cls._target_description(ant),
        )

    @staticmethod
    def _target_description(
        ant: Ant,
    ) -> str:
        if ant.food_target is not None:
            return f"Food {ant.food_target.id}"

        if ant.nest_target is not None:
            return "Nest"

        return "None"