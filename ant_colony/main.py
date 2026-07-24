import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui.inspector import Inspector
from ant_colony.ui.renderer import Renderer
from ant_colony.world import World


def main() -> None:
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (
                settings.SCREEN_WIDTH,
                settings.SCREEN_HEIGHT,
            )
        )

        pygame.display.set_caption(settings.WINDOW_TITLE)

        clock = pygame.time.Clock()
        camera = Camera()
        world = World()
        renderer = Renderer(screen, camera)
        inspector = Inspector()

        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    world_position = camera.screen_to_world(
                        *event.pos,
                    )
                    world.handle_click(world_position)

            world.update()

            renderer.draw(world)
            inspector.draw(
                screen,
                world.selected_ant,
            )

            pygame.display.flip()
            clock.tick(settings.FPS)

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()