"""Immutable snapshot of the world state at a single point in time.

:class:`WorldSnapshot` is safe to hand to renderers or observers that
must not modify the live world.  All collections it exposes are
immutable (``frozenset``, ``tuple``) or copies.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.terrain import TerrainType

if TYPE_CHECKING:
    pass


@dataclasses.dataclass(frozen=True)
class ResourceSnapshot:
    """Read-only view of a resource deposit."""

    coordinate: Coordinate
    amount: int
    max_amount: int

    @property
    def is_exhausted(self) -> bool:
        return self.amount == 0


@dataclasses.dataclass(frozen=True)
class WorldSnapshot:
    """A complete, immutable view of the world at one tick.

    Attributes:
        tick:         Tick number at the time this snapshot was taken.
        width:        Number of columns.
        height:       Number of rows.
        terrain:      Mapping of coordinate → :class:`~ant_colony.domain.terrain.TerrainType`.
                      Exposed as a ``dict`` copy – callers may read it freely.
        obstacle_coords: Frozen set of coordinates holding obstacles.
        resources:    Tuple of :class:`ResourceSnapshot` for every non-exhausted resource.
        nest_coord:   Location of the nest, or ``None`` if none was placed.
    """

    tick: int
    width: int
    height: int
    terrain: dict[Coordinate, TerrainType]
    obstacle_coords: frozenset[Coordinate]
    resources: tuple[ResourceSnapshot, ...]
    nest_coord: Coordinate | None

    def resource_at(self, coord: Coordinate) -> ResourceSnapshot | None:
        """Return the :class:`ResourceSnapshot` at *coord*, or ``None``."""
        for r in self.resources:
            if r.coordinate == coord:
                return r
        return None

    def has_obstacle_at(self, coord: Coordinate) -> bool:
        """Return ``True`` if an obstacle occupies *coord*."""
        return coord in self.obstacle_coords

    def terrain_at(self, coord: Coordinate) -> TerrainType:
        """Return the :class:`~ant_colony.domain.terrain.TerrainType` at *coord*."""
        return self.terrain.get(coord, TerrainType.OPEN)

    def to_text_grid(self) -> str:
        """Render the snapshot as a simple ASCII grid for debugging / demos.

        Legend::

            .  open cell
            #  wall terrain
            O  obstacle
            R  resource (non-exhausted)
            r  resource (exhausted)
            N  nest
        """
        active_resources = {s.coordinate for s in self.resources if not s.is_exhausted}
        exhausted_resources = {s.coordinate for s in self.resources if s.is_exhausted}
        lines: list[str] = []
        for row in range(self.height):
            cells: list[str] = []
            for col in range(self.width):
                coord = Coordinate(col, row)
                if coord in self.obstacle_coords:
                    cells.append("O")
                elif coord == self.nest_coord:
                    cells.append("N")
                elif coord in active_resources:
                    cells.append("R")
                elif coord in exhausted_resources:
                    cells.append("r")
                elif self.terrain.get(coord, TerrainType.OPEN) is TerrainType.WALL:
                    cells.append("#")
                else:
                    cells.append(".")
            lines.append(" ".join(cells))
        return "\n".join(lines)
