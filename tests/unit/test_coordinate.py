"""Unit tests for the Coordinate value object."""

from __future__ import annotations

import pytest

from ant_colony.domain.coordinate import Coordinate


class TestCoordinateCreation:
    def test_stores_x_and_y(self) -> None:
        c = Coordinate(3, 7)
        assert c.x == 3
        assert c.y == 7

    def test_zero_coordinate(self) -> None:
        c = Coordinate(0, 0)
        assert c.x == 0
        assert c.y == 0

    def test_negative_coordinates_allowed(self) -> None:
        """Coordinates outside bounds are valid objects; the World checks bounds."""
        c = Coordinate(-1, -5)
        assert c.x == -1
        assert c.y == -5

    def test_non_integer_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            Coordinate(1.5, 2)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            Coordinate(1, "2")  # type: ignore[arg-type]


class TestCoordinateImmutability:
    def test_cannot_set_attribute(self) -> None:
        c = Coordinate(1, 2)
        with pytest.raises(AttributeError):
            c.x = 99  # type: ignore[misc]

    def test_cannot_delete_attribute(self) -> None:
        c = Coordinate(1, 2)
        with pytest.raises(AttributeError):
            del c.x  # type: ignore[misc]


class TestCoordinateEquality:
    def test_equal_when_same_xy(self) -> None:
        assert Coordinate(3, 4) == Coordinate(3, 4)

    def test_not_equal_different_x(self) -> None:
        assert Coordinate(1, 4) != Coordinate(2, 4)

    def test_not_equal_different_y(self) -> None:
        assert Coordinate(3, 4) != Coordinate(3, 5)

    def test_not_equal_to_non_coordinate(self) -> None:
        assert Coordinate(1, 2) != (1, 2)
        assert Coordinate(1, 2) != "1,2"


class TestCoordinateHashing:
    def test_usable_as_dict_key(self) -> None:
        d: dict[Coordinate, int] = {}
        d[Coordinate(1, 2)] = 42
        assert d[Coordinate(1, 2)] == 42

    def test_usable_in_set(self) -> None:
        s = {Coordinate(0, 0), Coordinate(1, 1), Coordinate(0, 0)}
        assert len(s) == 2

    def test_equal_coordinates_same_hash(self) -> None:
        assert hash(Coordinate(5, 7)) == hash(Coordinate(5, 7))


class TestCoordinateUnpacking:
    def test_tuple_unpack(self) -> None:
        x, y = Coordinate(4, 9)
        assert x == 4
        assert y == 9


class TestManhattanDistance:
    def test_same_point(self) -> None:
        c = Coordinate(3, 3)
        assert c.manhattan_distance(c) == 0

    def test_horizontal(self) -> None:
        assert Coordinate(0, 0).manhattan_distance(Coordinate(5, 0)) == 5

    def test_vertical(self) -> None:
        assert Coordinate(0, 0).manhattan_distance(Coordinate(0, 3)) == 3

    def test_diagonal(self) -> None:
        assert Coordinate(0, 0).manhattan_distance(Coordinate(3, 4)) == 7


class TestNeighbors:
    def test_neighbors_4_count(self) -> None:
        assert len(Coordinate(5, 5).neighbors_4()) == 4

    def test_neighbors_4_values(self) -> None:
        neighbours = set(Coordinate(5, 5).neighbors_4())
        expected = {
            Coordinate(5, 4),
            Coordinate(6, 5),
            Coordinate(5, 6),
            Coordinate(4, 5),
        }
        assert neighbours == expected

    def test_neighbors_8_count(self) -> None:
        assert len(Coordinate(5, 5).neighbors_8()) == 8

    def test_neighbors_8_includes_diagonals(self) -> None:
        neighbours = set(Coordinate(5, 5).neighbors_8())
        assert Coordinate(4, 4) in neighbours
        assert Coordinate(6, 6) in neighbours
