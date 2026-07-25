"""Typed scenario configuration model.

A :class:`ScenarioConfig` is the in-memory representation of a
human-readable TOML scenario file.  It is intentionally *plain data*
(dataclasses) so that it can be validated, serialised, and diffed
without any domain coupling.
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class WallSpec:
    """A single WALL cell in the terrain grid."""

    x: int
    y: int


@dataclasses.dataclass(frozen=True)
class ObstacleSpec:
    """A single obstacle placed at ``(x, y)``."""

    x: int
    y: int


@dataclasses.dataclass(frozen=True)
class ResourceSpec:
    """A resource deposit placed at ``(x, y)``."""

    x: int
    y: int
    amount: int
    max_amount: int


@dataclasses.dataclass(frozen=True)
class NestSpec:
    """The colony nest location."""

    x: int
    y: int


@dataclasses.dataclass(frozen=True)
class WorldSpec:
    """The world section of a scenario configuration."""

    width: int
    height: int
    walls: tuple[WallSpec, ...]
    obstacles: tuple[ObstacleSpec, ...]
    resources: tuple[ResourceSpec, ...]
    nest: NestSpec | None


@dataclasses.dataclass(frozen=True)
class SimulationSpec:
    """The simulation section of a scenario configuration."""

    seed: int
    ticks: int


@dataclasses.dataclass(frozen=True)
class ScenarioConfig:
    """Complete scenario configuration loaded from a TOML file.

    Attributes:
        name:       Human-readable scenario identifier.
        world:      World geometry and object placement.
        simulation: Simulation parameters (seed, tick count).
    """

    name: str
    world: WorldSpec
    simulation: SimulationSpec
