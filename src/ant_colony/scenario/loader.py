"""Scenario loader – reads a TOML file and constructs a World + engine.

Usage::

    from ant_colony.scenario import ScenarioLoader

    config, engine = ScenarioLoader.load_file("scenarios/example.toml")

The loader validates the TOML structure eagerly and raises
:class:`~ant_colony.domain.errors.InvalidScenarioError` with a
descriptive message for any problem.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.errors import InvalidScenarioError
from ant_colony.domain.terrain import TerrainType
from ant_colony.domain.world import World
from ant_colony.scenario.config import (
    NestSpec,
    ObstacleSpec,
    ResourceSpec,
    ScenarioConfig,
    SimulationSpec,
    WallSpec,
    WorldSpec,
)
from ant_colony.simulation.engine import SimulationEngine


class ScenarioLoader:
    """Parses TOML scenario files and constructs the domain objects.

    All public methods are ``@staticmethod`` or ``@classmethod``; the
    class is a stateless namespace.
    """

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    @staticmethod
    def load_file(path: str | Path) -> tuple[ScenarioConfig, SimulationEngine]:
        """Load a scenario from a TOML file and return a ready engine.

        Args:
            path: Path to the ``.toml`` scenario file.

        Returns:
            A ``(config, engine)`` pair where *engine* has the world
            fully populated and ready to tick.

        Raises:
            InvalidScenarioError: On any structural or semantic error.
            FileNotFoundError:    If *path* does not exist.
        """
        resolved = Path(path)
        try:
            raw_bytes = resolved.read_bytes()
        except FileNotFoundError:
            raise FileNotFoundError(f"Scenario file not found: {path}") from None
        return ScenarioLoader.load_bytes(raw_bytes)

    @staticmethod
    def load_bytes(data: bytes) -> tuple[ScenarioConfig, SimulationEngine]:
        """Parse TOML *data* bytes and return a ready engine.

        Useful in tests where you want to avoid the filesystem.
        """
        try:
            raw: dict[str, Any] = tomllib.loads(data.decode())
        except tomllib.TOMLDecodeError as exc:
            raise InvalidScenarioError(f"Invalid TOML: {exc}") from exc

        config = ScenarioLoader._parse_config(raw)
        engine = ScenarioLoader._build_engine(config)
        return config, engine

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_config(raw: dict[str, Any]) -> ScenarioConfig:
        name = str(raw.get("name", "unnamed"))

        # -- world -------------------------------------------------------
        world_raw = raw.get("world")
        if not isinstance(world_raw, dict):
            raise InvalidScenarioError("Missing or invalid [world] section")

        width = ScenarioLoader._int(world_raw, "width", section="world")
        height = ScenarioLoader._int(world_raw, "height", section="world")
        if width < 1:
            raise InvalidScenarioError(f"world.width must be ≥ 1, got {width}")
        if height < 1:
            raise InvalidScenarioError(f"world.height must be ≥ 1, got {height}")

        # walls
        wall_raw = world_raw.get("walls", [])
        if not isinstance(wall_raw, list):
            raise InvalidScenarioError("world.walls must be an array")
        walls: list[WallSpec] = []
        for i, w in enumerate(wall_raw):
            if not isinstance(w, list) or len(w) != 2:
                raise InvalidScenarioError(f"world.walls[{i}] must be a two-element [x, y] array")
            walls.append(WallSpec(x=int(w[0]), y=int(w[1])))

        # obstacles
        obs_raw = world_raw.get("obstacles", [])
        if not isinstance(obs_raw, list):
            raise InvalidScenarioError("world.obstacles must be an array")
        obstacles: list[ObstacleSpec] = []
        for i, o in enumerate(obs_raw):
            if not isinstance(o, dict):
                raise InvalidScenarioError(f"world.obstacles[{i}] must be a table with x and y")
            obstacles.append(
                ObstacleSpec(
                    x=ScenarioLoader._int(o, "x", section=f"obstacles[{i}]"),
                    y=ScenarioLoader._int(o, "y", section=f"obstacles[{i}]"),
                )
            )

        # resources
        res_raw = world_raw.get("resources", [])
        if not isinstance(res_raw, list):
            raise InvalidScenarioError("world.resources must be an array")
        resources: list[ResourceSpec] = []
        for i, r in enumerate(res_raw):
            if not isinstance(r, dict):
                raise InvalidScenarioError(
                    f"world.resources[{i}] must be a table with x, y, and amount"
                )
            amount = ScenarioLoader._int(r, "amount", section=f"resources[{i}]")
            max_amount = int(r.get("max_amount", amount))
            resources.append(
                ResourceSpec(
                    x=ScenarioLoader._int(r, "x", section=f"resources[{i}]"),
                    y=ScenarioLoader._int(r, "y", section=f"resources[{i}]"),
                    amount=amount,
                    max_amount=max_amount,
                )
            )

        # nest
        nest_raw = world_raw.get("nest")
        nest: NestSpec | None = None
        if nest_raw is not None:
            if not isinstance(nest_raw, dict):
                raise InvalidScenarioError("world.nest must be a table with x and y")
            nest = NestSpec(
                x=ScenarioLoader._int(nest_raw, "x", section="nest"),
                y=ScenarioLoader._int(nest_raw, "y", section="nest"),
            )

        world_spec = WorldSpec(
            width=width,
            height=height,
            walls=tuple(walls),
            obstacles=tuple(obstacles),
            resources=tuple(resources),
            nest=nest,
        )

        # -- simulation --------------------------------------------------
        sim_raw = raw.get("simulation")
        if not isinstance(sim_raw, dict):
            raise InvalidScenarioError("Missing or invalid [simulation] section")

        seed = ScenarioLoader._int(sim_raw, "seed", section="simulation")
        ticks = int(sim_raw.get("ticks", 0))

        sim_spec = SimulationSpec(seed=seed, ticks=ticks)

        return ScenarioConfig(name=name, world=world_spec, simulation=sim_spec)

    @staticmethod
    def _build_engine(config: ScenarioConfig) -> SimulationEngine:
        ws = config.world
        world = World(width=ws.width, height=ws.height)

        # Apply walls first (before objects that depend on terrain)
        for w in ws.walls:
            coord = Coordinate(w.x, w.y)
            try:
                world.set_terrain(coord, TerrainType.WALL)
            except Exception as exc:
                raise InvalidScenarioError(f"Cannot place wall at ({w.x}, {w.y}): {exc}") from exc

        # Obstacles
        for o in ws.obstacles:
            coord = Coordinate(o.x, o.y)
            try:
                world.place_obstacle(coord)
            except Exception as exc:
                raise InvalidScenarioError(
                    f"Cannot place obstacle at ({o.x}, {o.y}): {exc}"
                ) from exc

        # Resources
        for r in ws.resources:
            coord = Coordinate(r.x, r.y)
            try:
                world.place_resource(coord, r.amount, r.max_amount)
            except Exception as exc:
                raise InvalidScenarioError(
                    f"Cannot place resource at ({r.x}, {r.y}): {exc}"
                ) from exc

        # Nest
        if ws.nest is not None:
            nest_coord = Coordinate(ws.nest.x, ws.nest.y)
            try:
                world.place_nest(nest_coord)
            except Exception as exc:
                raise InvalidScenarioError(
                    f"Cannot place nest at ({ws.nest.x}, {ws.nest.y}): {exc}"
                ) from exc

        return SimulationEngine(world=world, seed=config.simulation.seed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _int(mapping: dict[str, Any], key: str, *, section: str) -> int:
        value = mapping.get(key)
        if value is None:
            raise InvalidScenarioError(f"Missing required field '{key}' in [{section}]")
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise InvalidScenarioError(
                f"Field '{key}' in [{section}] must be an integer, got {value!r}"
            ) from exc
