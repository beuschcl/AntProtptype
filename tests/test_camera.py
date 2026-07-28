import pygame

from ant_colony.graphics.camera import Camera


def test_camera_converts_world_position_to_screen_position() -> None:
    camera = Camera()
    camera.x = 10
    camera.y = 20
    camera.zoom = 2

    assert camera.world_to_screen(15, 25) == (10, 10)


def test_camera_converts_screen_position_to_world_position() -> None:
    camera = Camera()
    camera.x = 10
    camera.y = 20
    camera.zoom = 2

    assert camera.screen_to_world(10, 10) == (15, 25)


def test_camera_scales_lengths() -> None:
    camera = Camera()
    camera.zoom = 2

    assert camera.scale_length(5) == 10


def test_camera_fits_world_inside_offset_viewport() -> None:
    camera = Camera()

    camera.fit(pygame.Rect(25, 40, 500, 350), (1000, 700))

    assert camera.zoom == 0.5
    assert camera.world_to_screen(0, 0) == (25, 40)
    assert camera.world_to_screen(1000, 700) == (525, 390)
    assert camera.screen_to_world(275, 215) == (500, 350)
