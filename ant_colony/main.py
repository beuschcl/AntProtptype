#ant_colony/main.py
import pygame

from ant_colony.config import settings
from ant_colony.ui.renderer import Renderer
from ant_colony.world import World
from ant_colony.ui.inspector import Inspector

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
    inspector = Inspector()
    clock = pygame.time.Clock()

    world = World()
    renderer = Renderer(screen)

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                world.handle_click(event.pos)

        world.update()

        renderer.draw(world)
        inspector.draw(
            screen,
            world.selected_ant,
        )

        pygame.display.flip()

        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()