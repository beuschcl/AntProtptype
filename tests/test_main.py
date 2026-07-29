import pytest

from ant_colony.config import settings
from ant_colony.graphics.camera import Camera
from ant_colony.main import _fit_camera_to_layout
from ant_colony.ui.window_layout import WindowLayout


def test_fit_camera_to_layout_updates_for_resized_viewports() -> None:
    camera = Camera()
    default_layout = WindowLayout.calculate(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        settings.INSPECTOR_WIDTH,
    )
    fullscreen_layout = WindowLayout.calculate((1920, 1080), settings.INSPECTOR_WIDTH)

    _fit_camera_to_layout(camera, default_layout)
    default_bottom_right = camera.screen_to_world(
        *default_layout.world_viewport.bottomright
    )

    _fit_camera_to_layout(camera, fullscreen_layout)
    fullscreen_bottom_right = camera.screen_to_world(
        *fullscreen_layout.world_viewport.bottomright
    )

    assert default_bottom_right == (settings.WORLD_WIDTH, settings.WORLD_HEIGHT)
    assert fullscreen_bottom_right[0] == pytest.approx(
        settings.WORLD_WIDTH,
        abs=0.2,
    )
    assert fullscreen_bottom_right[1] == pytest.approx(
        settings.WORLD_HEIGHT,
        abs=0.2,
    )


def test_fit_camera_to_layout_preserves_world_origin_for_click_mapping() -> None:
    camera = Camera()
    layout = WindowLayout.calculate((1400, 900), settings.INSPECTOR_WIDTH)

    _fit_camera_to_layout(camera, layout)

    assert camera.screen_to_world(*layout.world_viewport.topleft) == (0.0, 0.0)
