import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui.inspector import Inspector
from ant_colony.ui.renderer import Renderer
from ant_colony.ui.window_layout import WindowController
from ant_colony.world import World


def main() -> None:
    pygame.init()

    try:
        window = WindowController()
        screen = window.create_screen()

        pygame.display.set_caption(
            settings.WINDOW_TITLE
        )

        clock = pygame.time.Clock()
        camera = Camera()
        world = World()
        renderer = Renderer(
            screen,
            camera,
        )
        inspector = Inspector()

        running = True

        while running:
            layout = window.layout(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        screen = window.toggle_fullscreen()
                        renderer.set_screen(screen)
                    renderer.handle_event(event)
                elif event.type == pygame.VIDEORESIZE and not window.fullscreen:
                    window.windowed_size = (
                        max(event.w, settings.MIN_WINDOW_WIDTH),
                        max(event.h, settings.MIN_WINDOW_HEIGHT),
                    )
                    screen = pygame.display.set_mode(
                        window.windowed_size,
                        pygame.RESIZABLE,
                    )
                    renderer.set_screen(screen)
                elif window.handle_divider_event(event, layout):
                    continue
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and layout.world_viewport.collidepoint(event.pos)
                ):
                    world_position = (
                        camera.screen_to_world(
                            *event.pos,
                        )
                    )

                    world.handle_click(
                        world_position
                    )

            world.update()

            layout = window.layout(screen)
            renderer.draw(world, layout)
            inspector.draw(
                screen,
                world,
                layout,
            )

            pygame.display.flip()
            clock.tick(settings.FPS)

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
