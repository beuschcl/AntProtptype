from dataclasses import dataclass

type Color = tuple[int, int, int]
type Point = tuple[float, float]


@dataclass(frozen=True, slots=True)
class Circle:
    x: float
    y: float
    radius: float
    color: Color
    width: int = 0


@dataclass(frozen=True, slots=True)
class Ellipse:
    x: float
    y: float
    radius_x: float
    radius_y: float
    color: Color
    width: int = 0


@dataclass(frozen=True, slots=True)
class Polygon:
    points: tuple[Point, ...]
    color: Color
    width: int = 0


type Shape = Circle | Ellipse | Polygon
