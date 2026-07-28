import pygame

from ant_colony.config import settings
from ant_colony.ui.inspector_snapshot import (
    InspectorSnapshot,
)
from ant_colony.ui.window_layout import WindowLayout
from ant_colony.world import World


class Inspector:
    LINE_HEIGHT = 25
    SECTION_SPACING = 15
    TOP_PADDING = 20
    LEFT_PADDING = 20
    FONT_SIZE = 24

    def __init__(self) -> None:
        self.font = pygame.font.SysFont(
            None,
            self.FONT_SIZE,
        )

    def draw(
        self,
        screen: pygame.Surface,
        world: World,
        layout: WindowLayout | None = None,
    ) -> None:
        snapshot = InspectorSnapshot.from_world(world)

        x = (
            layout.inspector_rect.x if layout is not None else settings.WORLD_WIDTH
        ) + self.LEFT_PADDING
        y = self.TOP_PADDING

        y = self._draw_lines(
            screen=screen,
            lines=self._colony_lines(snapshot),
            x=x,
            y=y,
        )

        if snapshot.selected_ant_id is None:
            return

        y += self.SECTION_SPACING

        self._draw_lines(
            screen=screen,
            lines=self._selected_ant_lines(snapshot),
            x=x,
            y=y,
        )

    def _draw_lines(
        self,
        screen: pygame.Surface,
        lines: tuple[str, ...],
        x: int,
        y: int,
    ) -> int:
        for line in lines:
            text = self.font.render(
                line,
                True,
                settings.INSPECTOR_TEXT_COLOR,
            )

            screen.blit(
                text,
                (x, y),
            )

            y += self.LINE_HEIGHT

        return y

    @staticmethod
    def _colony_lines(
        snapshot: InspectorSnapshot,
    ) -> tuple[str, ...]:
        return (
            "Colony",
            f"Ants: {snapshot.ant_count}",
            (f"Food sources: {snapshot.food_source_count}"),
            (f"Food portions: {snapshot.remaining_food_portions}"),
            (f"Nest reserve: {snapshot.nest_food_reserve}"),
            (f"Delivered: {snapshot.delivered_portions}"),
            f"Pheromones: {snapshot.pheromone_count}",
        )

    @staticmethod
    def _selected_ant_lines(
        snapshot: InspectorSnapshot,
    ) -> tuple[str, ...]:
        return (
            "Selected Ant",
            f"ID: {snapshot.selected_ant_id}",
            (
                "Position: "
                f"({int(snapshot.selected_ant_x or 0)}, "
                f"{int(snapshot.selected_ant_y or 0)})"
            ),
            (f"Speed: {snapshot.selected_ant_speed or 0:.2f}"),
            (f"Heading: {snapshot.selected_ant_heading or 0:.1f}"),
            f"State: {snapshot.selected_ant_state}",
            (
                "Inventory: "
                f"{snapshot.selected_ant_inventory_count}/"
                f"{snapshot.selected_ant_inventory_capacity}"
            ),
            (f"Knowledge: {snapshot.selected_ant_knowledge_count}"),
            f"Target: {snapshot.selected_ant_target}",
            (
                "Hydration: "
                f"{snapshot.selected_ant_hydration or 0:.1f}"
                f"/{snapshot.selected_ant_hydration_max or 0:.1f}"
            ),
            (
                "Energy: "
                f"{snapshot.selected_ant_energy or 0}"
                f"/{snapshot.selected_ant_energy_max or 0}"
            ),
        )
