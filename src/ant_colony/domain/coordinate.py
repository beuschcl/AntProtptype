"""Immutable 2-D grid coordinate."""

from __future__ import annotations

from collections.abc import Iterator


class Coordinate:
    """An immutable integer (x, y) position on the square grid.

    ``x`` is the column index (left to right) and ``y`` is the row index
    (top to bottom), both zero-based.

    Because coordinates are used as dictionary keys and set members
    throughout the domain, the class is hashable and equality is
    value-based.
    """

    __slots__ = ("_x", "_y")
    _x: int
    _y: int

    def __init__(self, x: int, y: int) -> None:
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError(f"Coordinate requires integer values, got ({x!r}, {y!r})")
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    # ------------------------------------------------------------------
    # Prevent mutation
    # ------------------------------------------------------------------

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Coordinate is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Coordinate is immutable")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def x(self) -> int:
        """Column index (0-based, left to right)."""
        return self._x

    @property
    def y(self) -> int:
        """Row index (0-based, top to bottom)."""
        return self._y

    # ------------------------------------------------------------------
    # Equality & hashing
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Coordinate):
            return self._x == other._x and self._y == other._y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Coordinate(x={self._x}, y={self._y})"

    def __iter__(self) -> Iterator[int]:
        """Allow tuple unpacking: ``x, y = coord``."""
        yield self._x
        yield self._y

    def manhattan_distance(self, other: Coordinate) -> int:
        """Return the Manhattan distance to *other*."""
        return abs(self._x - other._x) + abs(self._y - other._y)

    def neighbors_4(self) -> tuple[Coordinate, ...]:
        """Return the four cardinal neighbours (may be outside world bounds)."""
        x = self._x
        y = self._y
        return (
            Coordinate(x, y - 1),
            Coordinate(x + 1, y),
            Coordinate(x, y + 1),
            Coordinate(x - 1, y),
        )

    def neighbors_8(self) -> tuple[Coordinate, ...]:
        """Return the eight cardinal + diagonal neighbours (may be outside world bounds)."""
        x = self._x
        y = self._y
        return (
            Coordinate(x, y - 1),
            Coordinate(x + 1, y - 1),
            Coordinate(x + 1, y),
            Coordinate(x + 1, y + 1),
            Coordinate(x, y + 1),
            Coordinate(x - 1, y + 1),
            Coordinate(x - 1, y),
            Coordinate(x - 1, y - 1),
        )
