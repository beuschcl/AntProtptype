"""Integration tests – scenario loading and full simulation runs."""

from __future__ import annotations

from pathlib import Path

import pytest

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.errors import InvalidScenarioError
from ant_colony.domain.events import ResourceDepleted, ResourceExhausted, TickAdvanced
from ant_colony.domain.terrain import TerrainType
from ant_colony.scenario.loader import ScenarioLoader

SCENARIOS_DIR = Path(__file__).parent.parent.parent / "scenarios"
EXAMPLE_TOML = SCENARIOS_DIR / "example.toml"


class TestExampleScenarioLoad:
    def test_loads_without_error(self) -> None:
        config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert config is not None
        assert engine is not None

    def test_world_dimensions(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert engine.world.width == 12
        assert engine.world.height == 10

    def test_nest_placed(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert engine.world.nest_coord == Coordinate(1, 5)

    def test_walls_placed(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert engine.world.terrain_at(Coordinate(5, 0)) is TerrainType.WALL
        assert engine.world.terrain_at(Coordinate(5, 3)) is TerrainType.WALL

    def test_obstacles_placed(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert engine.world.has_obstacle_at(Coordinate(2, 2))
        assert engine.world.has_obstacle_at(Coordinate(9, 7))

    def test_resources_placed(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        r1 = engine.world.resource_at(Coordinate(8, 2))
        r2 = engine.world.resource_at(Coordinate(3, 7))
        assert r1 is not None and r1.amount == 50
        assert r2 is not None and r2.amount == 30

    def test_seed_stored_in_config(self) -> None:
        config, _ = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert config.simulation.seed == 42

    def test_initial_tick_is_zero(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        assert engine.tick == 0


class TestSimulationRun:
    def test_tick_events_emitted(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        events = engine.advance_tick()
        tick_events = [e for e in events if isinstance(e, TickAdvanced)]
        assert tick_events[0].tick == 1

    def test_five_ticks(self) -> None:
        config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        for _ in range(config.simulation.ticks):
            engine.advance_tick()
        assert engine.tick == config.simulation.ticks

    def test_resource_depletion_events(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        events = engine.world.deplete_resource(Coordinate(8, 2), 20)
        depleted = [e for e in events if isinstance(e, ResourceDepleted)]
        assert len(depleted) == 1
        assert depleted[0].amount_depleted == 20
        assert depleted[0].remaining == 30

    def test_full_depletion_emits_exhausted(self) -> None:
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        events = engine.world.deplete_resource(Coordinate(8, 2), 50)
        exhausted = [e for e in events if isinstance(e, ResourceExhausted)]
        assert len(exhausted) == 1

    def test_snapshot_after_run(self) -> None:
        config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        for _ in range(config.simulation.ticks):
            engine.advance_tick()
        snap = engine.snapshot()
        assert snap.tick == config.simulation.ticks
        assert snap.width == 12
        assert snap.height == 10


class TestInvalidScenarios:
    def test_missing_world_section(self) -> None:
        toml = b"[simulation]\nseed = 1\nticks = 1\n"
        with pytest.raises(InvalidScenarioError, match="world"):
            ScenarioLoader.load_bytes(toml)

    def test_missing_simulation_section(self) -> None:
        toml = b"[world]\nwidth = 5\nheight = 5\n"
        with pytest.raises(InvalidScenarioError, match="simulation"):
            ScenarioLoader.load_bytes(toml)

    def test_invalid_dimensions(self) -> None:
        toml = b"[world]\nwidth = 0\nheight = 5\n[simulation]\nseed = 1\nticks = 1\n"
        with pytest.raises(InvalidScenarioError, match="width"):
            ScenarioLoader.load_bytes(toml)

    def test_obstacle_out_of_bounds(self) -> None:
        toml = (
            b"[world]\nwidth = 5\nheight = 5\n"
            b"[[world.obstacles]]\nx = 99\ny = 99\n"
            b"[simulation]\nseed = 1\nticks = 1\n"
        )
        with pytest.raises(InvalidScenarioError):
            ScenarioLoader.load_bytes(toml)

    def test_invalid_toml_raises(self) -> None:
        with pytest.raises(InvalidScenarioError, match="TOML"):
            ScenarioLoader.load_bytes(b"this is not valid toml !!!@@@")

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            ScenarioLoader.load_file("/nonexistent/path/scenario.toml")

    def test_load_bytes_minimal_scenario(self) -> None:
        toml = b"name = 'tiny'\n[world]\nwidth = 3\nheight = 3\n[simulation]\nseed = 0\nticks = 0\n"
        config, engine = ScenarioLoader.load_bytes(toml)
        assert config.name == "tiny"
        assert engine.world.width == 3
