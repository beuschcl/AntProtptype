#ant_colony/main.py
import pygame

from ant_colony.config import settings
from ant_colony.ui.renderer import Renderer
from ant_colony.world import World


def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            settings.SCREEN_WIDTH,
            settings.SCREEN_HEIGHT,
        )
    )

    pygame.display.set_caption(
        settings.WINDOW_TITLE
    )

    clock = pygame.time.Clock()

    world = World()
    renderer = Renderer(screen)

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        world.update()

        renderer.draw(world)

        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()