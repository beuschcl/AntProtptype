"""Terrain types for the world grid."""

from __future__ import annotations

import enum


class TerrainType(enum.Enum):
    """The terrain at a grid cell.

    ``OPEN`` cells may be entered by ants and can hold resources.
    ``WALL`` cells are impassable and cannot hold any world object.
    """

    OPEN = "open"
    WALL = "wall"

    @property
    def is_traversable(self) -> bool:
        """Return ``True`` when the terrain allows movement."""
        return self is TerrainType.OPEN
