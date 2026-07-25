"""The mutable world model – grid, occupancy, and all queries.

:class:`World` is the central domain aggregate.  It owns the terrain
grid, obstacle set, resource map, and nest location.  It enforces
invariants on placement and exposes neighbourhood queries used by future
simulation components.

Only :class:`~ant_colony.simulation.engine.SimulationEngine` and the
scenario loader should mutate a ``World`` after construction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.errors import (
    InvalidCoordinateError,
    NoResourceError,
    OccupancyConflictError,
    ResourceExhaustedError,
)
from ant_colony.domain.events import (
    AnyEvent,
    ResourceDepleted,
    ResourceExhausted,
)
from ant_colony.domain.snapshot import ResourceSnapshot, WorldSnapshot
from ant_colony.domain.terrain import TerrainType
from ant_colony.domain.world_objects import Nest, Obstacle, Resource

if TYPE_CHECKING:
    pass


class World:
    """A bounded square-grid world.

    Args:
        width:   Number of columns (must be ≥ 1).
        height:  Number of rows (must be ≥ 1).

    Raises:
        ValueError: If *width* or *height* are less than 1.
    """

    def __init__(self, width: int, height: int) -> None:
        if width < 1:
            raise ValueError(f"World width must be ≥ 1, got {width}")
        if height < 1:
            raise ValueError(f"World height must be ≥ 1, got {height}")
        self._width = width
        self._height = height
        self._terrain: dict[Coordinate, TerrainType] = {}
        self._obstacles: dict[Coordinate, Obstacle] = {}
        self._resources: dict[Coordinate, Resource] = {}
        self._nest: tuple[Coordinate, Nest] | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def width(self) -> int:
        """Number of columns."""
        return self._width

    @property
    def height(self) -> int:
        """Number of rows."""
        return self._height

    @property
    def nest_coord(self) -> Coordinate | None:
        """Location of the nest, or ``None`` if not placed."""
        return self._nest[0] if self._nest else None

    # ------------------------------------------------------------------
    # Coordinate validation
    # ------------------------------------------------------------------

    def is_valid_coordinate(self, coord: Coordinate) -> bool:
        """Return ``True`` if *coord* is within world bounds."""
        return 0 <= coord.x < self._width and 0 <= coord.y < self._height

    def _require_valid(self, coord: Coordinate) -> None:
        if not self.is_valid_coordinate(coord):
            raise InvalidCoordinateError(coord.x, coord.y, self._width, self._height)

    # ------------------------------------------------------------------
    # Terrain
    # ------------------------------------------------------------------

    def set_terrain(self, coord: Coordinate, terrain: TerrainType) -> None:
        """Set the terrain at *coord*.

        Raises:
            InvalidCoordinateError: If *coord* is out of bounds.
            OccupancyConflictError: If *coord* already holds an object
                                    that is incompatible with WALL terrain.
        """
        self._require_valid(coord)
        if terrain is TerrainType.WALL:
            # Walls cannot coexist with obstacles, resources, or the nest.
            if coord in self._obstacles:
                raise OccupancyConflictError(coord.x, coord.y, "obstacle", "wall terrain")
            if coord in self._resources:
                raise OccupancyConflictError(coord.x, coord.y, "resource", "wall terrain")
            if self._nest and self._nest[0] == coord:
                raise OccupancyConflictError(coord.x, coord.y, "nest", "wall terrain")
        self._terrain[coord] = terrain

    def terrain_at(self, coord: Coordinate) -> TerrainType:
        """Return the terrain at *coord* (default: ``OPEN``)."""
        return self._terrain.get(coord, TerrainType.OPEN)

    def is_traversable(self, coord: Coordinate) -> bool:
        """Return ``True`` if *coord* is within bounds and traversable.

        A cell is traversable when its terrain is ``OPEN`` **and** it
        contains no ``Obstacle``.
        """
        if not self.is_valid_coordinate(coord):
            return False
        if self._terrain.get(coord, TerrainType.OPEN) is TerrainType.WALL:
            return False
        return coord not in self._obstacles

    # ------------------------------------------------------------------
    # Obstacles
    # ------------------------------------------------------------------

    def place_obstacle(self, coord: Coordinate) -> None:
        """Place an :class:`~ant_colony.domain.world_objects.Obstacle` at *coord*.

        Raises:
            InvalidCoordinateError: If *coord* is out of bounds.
            OccupancyConflictError: If the cell already holds an
                                    incompatible object (obstacle, resource,
                                    nest) or has WALL terrain.
        """
        self._require_valid(coord)
        if self._terrain.get(coord, TerrainType.OPEN) is TerrainType.WALL:
            raise OccupancyConflictError(coord.x, coord.y, "wall terrain", "obstacle")
        if coord in self._obstacles:
            raise OccupancyConflictError(coord.x, coord.y, "obstacle", "obstacle")
        if coord in self._resources:
            raise OccupancyConflictError(coord.x, coord.y, "resource", "obstacle")
        if self._nest and self._nest[0] == coord:
            raise OccupancyConflictError(coord.x, coord.y, "nest", "obstacle")
        self._obstacles[coord] = Obstacle()

    def has_obstacle_at(self, coord: Coordinate) -> bool:
        """Return ``True`` if an obstacle occupies *coord*."""
        return coord in self._obstacles

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def place_resource(self, coord: Coordinate, amount: int, max_amount: int | None = None) -> None:
        """Place a :class:`~ant_colony.domain.world_objects.Resource` at *coord*.

        Raises:
            InvalidCoordinateError: If *coord* is out of bounds.
            OccupancyConflictError: If the cell already holds an
                                    incompatible object or has WALL terrain.
            ValueError:             If *amount* / *max_amount* are invalid.
        """
        self._require_valid(coord)
        if self._terrain.get(coord, TerrainType.OPEN) is TerrainType.WALL:
            raise OccupancyConflictError(coord.x, coord.y, "wall terrain", "resource")
        if coord in self._obstacles:
            raise OccupancyConflictError(coord.x, coord.y, "obstacle", "resource")
        if coord in self._resources:
            raise OccupancyConflictError(coord.x, coord.y, "resource", "resource")
        self._resources[coord] = Resource(amount, max_amount)

    def resource_at(self, coord: Coordinate) -> Resource | None:
        """Return the :class:`~ant_colony.domain.world_objects.Resource` at *coord*, or ``None``."""
        return self._resources.get(coord)

    def deplete_resource(self, coord: Coordinate, amount: int) -> list[AnyEvent]:
        """Remove *amount* from the resource at *coord*.

        Args:
            coord:  Location of the resource.
            amount: Quantity to remove (must be positive).

        Returns:
            A list of :data:`~ant_colony.domain.events.AnyEvent` that
            describes what changed:

            * Always includes a :class:`~ant_colony.domain.events.ResourceDepleted`.
            * Appends a :class:`~ant_colony.domain.events.ResourceExhausted`
              when the deposit reaches zero.

        Raises:
            InvalidCoordinateError: If *coord* is out of bounds.
            NoResourceError:        If no resource exists at *coord*.
            ResourceExhaustedError: If the resource is already at zero.
            ValueError:             If *amount* is not positive.
        """
        self._require_valid(coord)
        resource = self._resources.get(coord)
        if resource is None:
            raise NoResourceError(coord.x, coord.y)
        if resource.is_exhausted:
            raise ResourceExhaustedError(coord.x, coord.y)
        removed = resource._deplete(amount)
        events: list[AnyEvent] = [
            ResourceDepleted(
                coordinate=coord,
                amount_depleted=removed,
                remaining=resource.amount,
            )
        ]
        if resource.is_exhausted:
            events.append(ResourceExhausted(coordinate=coord))
        return events

    # ------------------------------------------------------------------
    # Nest
    # ------------------------------------------------------------------

    def place_nest(self, coord: Coordinate) -> None:
        """Mark *coord* as the colony nest location.

        Only one nest may exist at a time.  The nest may share a cell
        with a resource (future ants drop resources at the nest).

        Raises:
            InvalidCoordinateError: If *coord* is out of bounds.
            OccupancyConflictError: If the cell has WALL terrain, holds
                                    an obstacle, or a nest already exists.
        """
        self._require_valid(coord)
        if self._terrain.get(coord, TerrainType.OPEN) is TerrainType.WALL:
            raise OccupancyConflictError(coord.x, coord.y, "wall terrain", "nest")
        if coord in self._obstacles:
            raise OccupancyConflictError(coord.x, coord.y, "obstacle", "nest")
        if self._nest is not None:
            existing_coord = self._nest[0]
            raise OccupancyConflictError(existing_coord.x, existing_coord.y, "nest", "nest")
        self._nest = (coord, Nest())

    # ------------------------------------------------------------------
    # Spatial queries
    # ------------------------------------------------------------------

    def get_neighbors(
        self, coord: Coordinate, *, include_diagonals: bool = False
    ) -> frozenset[Coordinate]:
        """Return valid in-bounds neighbours of *coord*.

        Args:
            coord:             Centre coordinate.
            include_diagonals: When ``True`` returns up to 8 neighbours;
                               otherwise returns up to 4 cardinal
                               neighbours.

        Returns:
            A :class:`frozenset` of :class:`Coordinate` that are within
            world bounds.
        """
        self._require_valid(coord)
        candidates = coord.neighbors_8() if include_diagonals else coord.neighbors_4()
        return frozenset(c for c in candidates if self.is_valid_coordinate(c))

    def get_traversable_neighbors(
        self, coord: Coordinate, *, include_diagonals: bool = False
    ) -> frozenset[Coordinate]:
        """Return traversable in-bounds neighbours of *coord*."""
        return frozenset(
            c
            for c in self.get_neighbors(coord, include_diagonals=include_diagonals)
            if self.is_traversable(c)
        )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def take_snapshot(self, tick: int = 0) -> WorldSnapshot:
        """Return an immutable :class:`~ant_colony.domain.snapshot.WorldSnapshot`.

        The snapshot captures a deep-enough copy that mutations to the
        live world do not affect it.

        Args:
            tick: Tick number to embed in the snapshot (default 0).
        """
        terrain_copy: dict[Coordinate, TerrainType] = dict(self._terrain)
        obstacle_coords = frozenset(self._obstacles.keys())
        resource_snaps = tuple(
            ResourceSnapshot(
                coordinate=coord,
                amount=res.amount,
                max_amount=res.max_amount,
            )
            for coord, res in self._resources.items()
        )
        nest_coord = self._nest[0] if self._nest else None
        return WorldSnapshot(
            tick=tick,
            width=self._width,
            height=self._height,
            terrain=terrain_copy,
            obstacle_coords=obstacle_coords,
            resources=resource_snaps,
            nest_coord=nest_coord,
        )

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"World(width={self._width}, height={self._height}, "
            f"obstacles={len(self._obstacles)}, "
            f"resources={len(self._resources)}, "
            f"nest={'yes' if self._nest else 'no'})"
        )
