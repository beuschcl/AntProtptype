import pytest

from ant_colony.graphics.primitives import Circle, Polygon


def test_circle_is_immutable() -> None:
    circle = Circle(
        x=10,
        y=20,
        radius=5,
        color=(255, 255, 255),
    )

    with pytest.raises(AttributeError):
        circle.radius = 10


def test_polygon_points_are_immutable() -> None:
    polygon = Polygon(
        points=(
            (0, 0),
            (10, 0),
            (5, 10),
        ),
        color=(255, 255, 255),
    )

    assert isinstance(polygon.points, tuple)