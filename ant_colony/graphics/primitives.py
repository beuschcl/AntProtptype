#ant_colony/graphics/primitives.py
from dataclasses import dataclass


@dataclass(slots=True)
class Circle:

    x: float
    y: float
    radius: float
    color: tuple[int, int, int]


@dataclass(slots=True)
class Polygon:

    points: list[tuple[float, float]]
    color: tuple[int, int, int]