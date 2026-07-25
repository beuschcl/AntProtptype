"""Domain package – exported public surface.

Importing from ``ant_colony.domain`` gives you everything you need
to build and inspect a world without touching simulation or I/O
concerns.
"""

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.errors import (
    AntColonyError,
    InvalidCoordinateError,
    InvalidScenarioError,
    NoResourceError,
    OccupancyConflictError,
    ResourceExhaustedError,
)
from ant_colony.domain.events import (
    AnyEvent,
    ResourceDepleted,
    ResourceExhausted,
    TickAdvanced,
    WorldEvent,
)
from ant_colony.domain.snapshot import ResourceSnapshot, WorldSnapshot
from ant_colony.domain.terrain import TerrainType
from ant_colony.domain.world import World
from ant_colony.domain.world_objects import Nest, Obstacle, Resource, WorldObject

__all__ = [
    "AntColonyError",
    "AnyEvent",
    "Coordinate",
    "InvalidCoordinateError",
    "InvalidScenarioError",
    "Nest",
    "NoResourceError",
    "Obstacle",
    "OccupancyConflictError",
    "Resource",
    "ResourceDepleted",
    "ResourceExhausted",
    "ResourceExhaustedError",
    "ResourceSnapshot",
    "TerrainType",
    "TickAdvanced",
    "World",
    "WorldEvent",
    "WorldObject",
    "WorldSnapshot",
]
