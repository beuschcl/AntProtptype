import random as _random_module

import pygame

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.ui.completion_overlay import CompletionOverlay
from ant_colony.ui.inspector import Inspector
from ant_colony.ui.renderer import Renderer
from ant_colony.ui.window_layout import WindowController
from ant_colony.world import World


def main() -> None:
    pygame.init()

    try:
        world_seed = _random_module.randrange(2**32)
        window = WindowController()
        screen = window.create_screen()

        pygame.display.set_caption(
            settings.WINDOW_TITLE
        )

        clock = pygame.time.Clock()
        camera = Camera()
        world = World(rng=_random_module.Random(world_seed))
        renderer = Renderer(
            screen,
            camera,
        )
        inspector = Inspector()
        completion_overlay = CompletionOverlay()

        running = True

        while running:
            layout = window.layout(screen)
            world_restarted = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif world.is_complete:
                    action = completion_overlay.handle_event(event)
                    if action == "restart":
                        world = World(rng=_random_module.Random(world_seed))
                        world_restarted = True
                    elif action == "exit":
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

            if not world.is_complete and not world_restarted:
                world.update()

            layout = window.layout(screen)
            renderer.draw(world, layout)

            if world.is_complete:
                completion_overlay.draw(screen, layout)

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
