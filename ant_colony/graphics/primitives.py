#ant_colony/graphics/primitives.py
from dataclasses import dataclass
from typing import TypeAlias

Color: TypeAlias = tuple[int, int, int]
Point: TypeAlias = tuple[float, float]


@dataclass(frozen=True, slots=True)
class Circle:
    x: float
    y: float
    radius: float
    color: Color
    width: int = 0


@dataclass(frozen=True, slots=True)
class Polygon:
    points: tuple[Point, ...]
    color: Color
    width: int = 0


Shape: TypeAlias = Circle | Polygon