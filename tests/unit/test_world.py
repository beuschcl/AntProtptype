"""Unit tests for the World aggregate."""

from __future__ import annotations

import pytest

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.errors import (
    InvalidCoordinateError,
    NoResourceError,
    OccupancyConflictError,
    ResourceExhaustedError,
)
from ant_colony.domain.events import ResourceDepleted, ResourceExhausted
from ant_colony.domain.terrain import TerrainType
from ant_colony.domain.world import World


@pytest.fixture()
def world5() -> World:
    """A 5x5 world for convenience."""
    return World(5, 5)


class TestWorldCreation:
    def test_dimensions(self) -> None:
        w = World(10, 8)
        assert w.width == 10
        assert w.height == 8

    def test_zero_width_raises(self) -> None:
        with pytest.raises(ValueError):
            World(0, 5)

    def test_zero_height_raises(self) -> None:
        with pytest.raises(ValueError):
            World(5, 0)

    def test_no_nest_initially(self) -> None:
        assert World(5, 5).nest_coord is None


class TestValidCoordinate:
    def test_corner_valid(self, world5: World) -> None:
        assert world5.is_valid_coordinate(Coordinate(0, 0))
        assert world5.is_valid_coordinate(Coordinate(4, 4))

    def test_outside_right_invalid(self, world5: World) -> None:
        assert not world5.is_valid_coordinate(Coordinate(5, 0))

    def test_outside_bottom_invalid(self, world5: World) -> None:
        assert not world5.is_valid_coordinate(Coordinate(0, 5))

    def test_negative_invalid(self, world5: World) -> None:
        assert not world5.is_valid_coordinate(Coordinate(-1, 0))


class TestTerrain:
    def test_default_terrain_is_open(self, world5: World) -> None:
        assert world5.terrain_at(Coordinate(2, 2)) is TerrainType.OPEN

    def test_set_wall(self, world5: World) -> None:
        world5.set_terrain(Coordinate(1, 1), TerrainType.WALL)
        assert world5.terrain_at(Coordinate(1, 1)) is TerrainType.WALL

    def test_set_terrain_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.set_terrain(Coordinate(99, 0), TerrainType.WALL)

    def test_wall_terrain_blocks_traversal(self, world5: World) -> None:
        world5.set_terrain(Coordinate(3, 3), TerrainType.WALL)
        assert not world5.is_traversable(Coordinate(3, 3))

    def test_out_of_bounds_not_traversable(self, world5: World) -> None:
        assert not world5.is_traversable(Coordinate(10, 10))


class TestObstacles:
    def test_place_obstacle(self, world5: World) -> None:
        world5.place_obstacle(Coordinate(2, 2))
        assert world5.has_obstacle_at(Coordinate(2, 2))

    def test_obstacle_blocks_traversal(self, world5: World) -> None:
        world5.place_obstacle(Coordinate(2, 2))
        assert not world5.is_traversable(Coordinate(2, 2))

    def test_open_cell_is_traversable(self, world5: World) -> None:
        assert world5.is_traversable(Coordinate(2, 2))

    def test_duplicate_obstacle_raises(self, world5: World) -> None:
        world5.place_obstacle(Coordinate(1, 1))
        with pytest.raises(OccupancyConflictError):
            world5.place_obstacle(Coordinate(1, 1))

    def test_obstacle_on_wall_raises(self, world5: World) -> None:
        world5.set_terrain(Coordinate(3, 3), TerrainType.WALL)
        with pytest.raises(OccupancyConflictError):
            world5.place_obstacle(Coordinate(3, 3))

    def test_obstacle_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.place_obstacle(Coordinate(99, 0))

    def test_obstacle_on_resource_raises(self, world5: World) -> None:
        world5.place_resource(Coordinate(2, 2), 10)
        with pytest.raises(OccupancyConflictError):
            world5.place_obstacle(Coordinate(2, 2))


class TestResources:
    def test_place_resource(self, world5: World) -> None:
        world5.place_resource(Coordinate(3, 3), 50)
        r = world5.resource_at(Coordinate(3, 3))
        assert r is not None
        assert r.amount == 50

    def test_resource_does_not_block_traversal(self, world5: World) -> None:
        world5.place_resource(Coordinate(3, 3), 50)
        assert world5.is_traversable(Coordinate(3, 3))

    def test_resource_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.place_resource(Coordinate(99, 0), 10)

    def test_resource_on_wall_raises(self, world5: World) -> None:
        world5.set_terrain(Coordinate(1, 1), TerrainType.WALL)
        with pytest.raises(OccupancyConflictError):
            world5.place_resource(Coordinate(1, 1), 10)

    def test_duplicate_resource_raises(self, world5: World) -> None:
        world5.place_resource(Coordinate(1, 1), 10)
        with pytest.raises(OccupancyConflictError):
            world5.place_resource(Coordinate(1, 1), 20)

    def test_resource_on_obstacle_raises(self, world5: World) -> None:
        world5.place_obstacle(Coordinate(2, 2))
        with pytest.raises(OccupancyConflictError):
            world5.place_resource(Coordinate(2, 2), 10)


class TestResourceDepletion:
    def test_partial_depletion(self, world5: World) -> None:
        world5.place_resource(Coordinate(2, 2), 100)
        events = world5.deplete_resource(Coordinate(2, 2), 30)
        assert len(events) == 1
        depleted_event = events[0]
        assert isinstance(depleted_event, ResourceDepleted)
        assert depleted_event.amount_depleted == 30
        assert depleted_event.remaining == 70

    def test_full_depletion_emits_exhausted_event(self, world5: World) -> None:
        world5.place_resource(Coordinate(2, 2), 50)
        events = world5.deplete_resource(Coordinate(2, 2), 50)
        assert len(events) == 2
        assert isinstance(events[0], ResourceDepleted)
        assert isinstance(events[1], ResourceExhausted)

    def test_over_depletion_caps_and_emits_exhausted(self, world5: World) -> None:
        world5.place_resource(Coordinate(2, 2), 10)
        events = world5.deplete_resource(Coordinate(2, 2), 999)
        exhausted_events = [e for e in events if isinstance(e, ResourceExhausted)]
        assert len(exhausted_events) == 1

    def test_no_resource_raises(self, world5: World) -> None:
        with pytest.raises(NoResourceError):
            world5.deplete_resource(Coordinate(2, 2), 10)

    def test_already_exhausted_raises(self, world5: World) -> None:
        world5.place_resource(Coordinate(2, 2), 10)
        world5.deplete_resource(Coordinate(2, 2), 10)
        with pytest.raises(ResourceExhaustedError):
            world5.deplete_resource(Coordinate(2, 2), 1)

    def test_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.deplete_resource(Coordinate(99, 0), 10)


class TestNest:
    def test_place_nest(self, world5: World) -> None:
        world5.place_nest(Coordinate(1, 1))
        assert world5.nest_coord == Coordinate(1, 1)

    def test_second_nest_raises(self, world5: World) -> None:
        world5.place_nest(Coordinate(1, 1))
        with pytest.raises(OccupancyConflictError):
            world5.place_nest(Coordinate(2, 2))

    def test_nest_on_wall_raises(self, world5: World) -> None:
        world5.set_terrain(Coordinate(3, 3), TerrainType.WALL)
        with pytest.raises(OccupancyConflictError):
            world5.place_nest(Coordinate(3, 3))

    def test_nest_on_obstacle_raises(self, world5: World) -> None:
        world5.place_obstacle(Coordinate(3, 3))
        with pytest.raises(OccupancyConflictError):
            world5.place_nest(Coordinate(3, 3))

    def test_nest_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.place_nest(Coordinate(99, 0))

    def test_nest_coexists_with_resource(self, world5: World) -> None:
        """Nest and resource can share a cell (ants drop food at nest)."""
        world5.place_resource(Coordinate(2, 2), 10)
        world5.place_nest(Coordinate(2, 2))  # should not raise
        assert world5.nest_coord == Coordinate(2, 2)


class TestNeighborhood:
    def test_four_neighbors_center(self) -> None:
        w = World(10, 10)
        nb = w.get_neighbors(Coordinate(5, 5))
        assert len(nb) == 4

    def test_four_neighbors_corner(self) -> None:
        w = World(10, 10)
        nb = w.get_neighbors(Coordinate(0, 0))
        assert len(nb) == 2

    def test_eight_neighbors_center(self) -> None:
        w = World(10, 10)
        nb = w.get_neighbors(Coordinate(5, 5), include_diagonals=True)
        assert len(nb) == 8

    def test_eight_neighbors_corner(self) -> None:
        w = World(10, 10)
        nb = w.get_neighbors(Coordinate(0, 0), include_diagonals=True)
        assert len(nb) == 3

    def test_traversable_neighbors_exclude_walls(self) -> None:
        w = World(10, 10)
        w.set_terrain(Coordinate(5, 4), TerrainType.WALL)
        traversable = w.get_traversable_neighbors(Coordinate(5, 5))
        assert Coordinate(5, 4) not in traversable

    def test_traversable_neighbors_exclude_obstacles(self) -> None:
        w = World(10, 10)
        w.place_obstacle(Coordinate(5, 4))
        traversable = w.get_traversable_neighbors(Coordinate(5, 5))
        assert Coordinate(5, 4) not in traversable

    def test_neighbors_out_of_bounds_raises(self, world5: World) -> None:
        with pytest.raises(InvalidCoordinateError):
            world5.get_neighbors(Coordinate(99, 0))


class TestSnapshot:
    def test_snapshot_captures_terrain(self) -> None:
        w = World(5, 5)
        w.set_terrain(Coordinate(2, 2), TerrainType.WALL)
        snap = w.take_snapshot(tick=1)
        assert snap.terrain.get(Coordinate(2, 2)) is TerrainType.WALL

    def test_snapshot_captures_resources(self) -> None:
        w = World(5, 5)
        w.place_resource(Coordinate(3, 3), 50)
        snap = w.take_snapshot()
        r = snap.resource_at(Coordinate(3, 3))
        assert r is not None
        assert r.amount == 50

    def test_snapshot_captures_nest(self) -> None:
        w = World(5, 5)
        w.place_nest(Coordinate(1, 1))
        snap = w.take_snapshot()
        assert snap.nest_coord == Coordinate(1, 1)

    def test_snapshot_captures_obstacles(self) -> None:
        w = World(5, 5)
        w.place_obstacle(Coordinate(4, 4))
        snap = w.take_snapshot()
        assert snap.has_obstacle_at(Coordinate(4, 4))

    def test_snapshot_immutable_terrain(self) -> None:
        """Mutating the snapshot's terrain dict must not affect the world."""
        w = World(5, 5)
        w.set_terrain(Coordinate(1, 1), TerrainType.WALL)
        snap = w.take_snapshot()
        snap.terrain[Coordinate(0, 0)] = TerrainType.WALL
        assert w.terrain_at(Coordinate(0, 0)) is TerrainType.OPEN

    def test_snapshot_immutable_obstacle_frozenset(self) -> None:
        w = World(5, 5)
        w.place_obstacle(Coordinate(1, 1))
        snap = w.take_snapshot()
        # frozenset is inherently immutable
        with pytest.raises((AttributeError, TypeError)):
            snap.obstacle_coords.add(Coordinate(2, 2))  # type: ignore[attr-defined]

    def test_snapshot_does_not_reflect_later_changes(self) -> None:
        w = World(5, 5)
        w.place_resource(Coordinate(2, 2), 100)
        snap_before = w.take_snapshot(tick=0)
        w.deplete_resource(Coordinate(2, 2), 50)
        # The pre-depletion snapshot still shows amount=100
        r = snap_before.resource_at(Coordinate(2, 2))
        assert r is not None
        assert r.amount == 100
