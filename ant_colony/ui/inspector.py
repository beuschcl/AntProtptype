import pygame

from ant_colony.config import settings
from ant_colony.entities.ant import Ant


class Inspector:
    LINE_HEIGHT = 25
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
        ant: Ant | None,
    ) -> None:
        if ant is None:
            return

        lines = (
            f"ID: {ant.id}",
            f"Position: ({int(ant.x)}, {int(ant.y)})",
            f"Speed: {ant.speed:.2f}",
            f"Heading: {ant.heading:.1f}",
            f"State: {ant.state.value}",
            f"Knowledge: {ant.knowledge.count()}",
        )

        x = settings.WORLD_WIDTH + self.LEFT_PADDING
        y = self.TOP_PADDING

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