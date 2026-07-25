"""Unit tests for WorldSnapshot."""

from __future__ import annotations

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.snapshot import ResourceSnapshot, WorldSnapshot
from ant_colony.domain.terrain import TerrainType


def _make_snapshot(**kwargs: object) -> WorldSnapshot:
    defaults: dict[str, object] = {
        "tick": 0,
        "width": 5,
        "height": 5,
        "terrain": {},
        "obstacle_coords": frozenset(),
        "resources": (),
        "nest_coord": None,
    }
    defaults.update(kwargs)
    return WorldSnapshot(**defaults)  # type: ignore[arg-type]


class TestWorldSnapshotDefaults:
    def test_no_nest(self) -> None:
        snap = _make_snapshot()
        assert snap.nest_coord is None

    def test_no_resource_at_any_coord(self) -> None:
        snap = _make_snapshot()
        assert snap.resource_at(Coordinate(2, 2)) is None

    def test_no_obstacle(self) -> None:
        snap = _make_snapshot()
        assert not snap.has_obstacle_at(Coordinate(0, 0))

    def test_default_terrain_is_open(self) -> None:
        snap = _make_snapshot()
        assert snap.terrain_at(Coordinate(3, 3)) is TerrainType.OPEN


class TestWorldSnapshotQueries:
    def test_resource_at_returns_correct(self) -> None:
        coord = Coordinate(2, 3)
        snap = _make_snapshot(
            resources=(ResourceSnapshot(coordinate=coord, amount=30, max_amount=50),)
        )
        r = snap.resource_at(coord)
        assert r is not None
        assert r.amount == 30

    def test_resource_at_wrong_coord_returns_none(self) -> None:
        coord = Coordinate(2, 3)
        snap = _make_snapshot(
            resources=(ResourceSnapshot(coordinate=coord, amount=30, max_amount=50),)
        )
        assert snap.resource_at(Coordinate(0, 0)) is None

    def test_has_obstacle_at(self) -> None:
        coord = Coordinate(1, 1)
        snap = _make_snapshot(obstacle_coords=frozenset({coord}))
        assert snap.has_obstacle_at(coord)
        assert not snap.has_obstacle_at(Coordinate(2, 2))

    def test_terrain_at_wall(self) -> None:
        coord = Coordinate(3, 3)
        snap = _make_snapshot(terrain={coord: TerrainType.WALL})
        assert snap.terrain_at(coord) is TerrainType.WALL


class TestTextGrid:
    def test_open_cells_show_dot(self) -> None:
        snap = _make_snapshot(width=3, height=3)
        grid = snap.to_text_grid()
        for char in grid:
            assert char in ". \n"

    def test_wall_shows_hash(self) -> None:
        coord = Coordinate(1, 1)
        snap = _make_snapshot(width=3, height=3, terrain={coord: TerrainType.WALL})
        lines = snap.to_text_grid().split("\n")
        assert lines[1].split()[1] == "#"

    def test_obstacle_shows_capital_o(self) -> None:
        coord = Coordinate(0, 0)
        snap = _make_snapshot(width=3, height=3, obstacle_coords=frozenset({coord}))
        lines = snap.to_text_grid().split("\n")
        assert lines[0].split()[0] == "O"

    def test_nest_shows_capital_n(self) -> None:
        coord = Coordinate(2, 2)
        snap = _make_snapshot(width=3, height=3, nest_coord=coord)
        lines = snap.to_text_grid().split("\n")
        assert lines[2].split()[2] == "N"

    def test_resource_shows_capital_r(self) -> None:
        coord = Coordinate(1, 0)
        snap = _make_snapshot(
            width=3,
            height=3,
            resources=(ResourceSnapshot(coordinate=coord, amount=10, max_amount=10),),
        )
        lines = snap.to_text_grid().split("\n")
        assert lines[0].split()[1] == "R"

    def test_exhausted_resource_shows_lowercase_r(self) -> None:
        coord = Coordinate(1, 0)
        snap = _make_snapshot(
            width=3,
            height=3,
            resources=(ResourceSnapshot(coordinate=coord, amount=0, max_amount=10),),
        )
        lines = snap.to_text_grid().split("\n")
        assert lines[0].split()[1] == "r"
