#ant_colony/ui/inspector.py
import pygame


class Inspector:

    def __init__(self):

        self.font = pygame.font.SysFont(
            None,
            24,
        )

    def draw(self, screen, ant):

        if ant is None:
            return

        lines = [
            f"ID: {ant.id}",
            f"Position: ({int(ant.x)}, {int(ant.y)})",
            f"Speed: {ant.speed:.2f}",
            f"Heading: {ant.heading:.1f}",
            f"State: {ant.state.value}",
            f"Knowledge: {ant.knowledge.count()}",
        ]

        y = 20

        for line in lines:

            text = self.font.render(
                line,
                True,
                (255, 255, 255),
            )

            screen.blit(
                text,
                (20, y),
            )

            y += 25