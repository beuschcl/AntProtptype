"""Unit tests for SimulationEngine."""

from __future__ import annotations

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.events import TickAdvanced
from ant_colony.domain.world import World
from ant_colony.simulation.engine import SimulationEngine


def _simple_engine(seed: int = 42) -> SimulationEngine:
    w = World(5, 5)
    w.place_nest(Coordinate(0, 0))
    w.place_resource(Coordinate(4, 4), 100)
    return SimulationEngine(world=w, seed=seed)


class TestSimulationEngineBasics:
    def test_initial_tick_is_zero(self) -> None:
        engine = _simple_engine()
        assert engine.tick == 0

    def test_advance_increments_tick(self) -> None:
        engine = _simple_engine()
        engine.advance_tick()
        assert engine.tick == 1

    def test_advance_multiple(self) -> None:
        engine = _simple_engine()
        for _ in range(10):
            engine.advance_tick()
        assert engine.tick == 10

    def test_advance_returns_tick_advanced_event(self) -> None:
        engine = _simple_engine()
        events = engine.advance_tick()
        tick_events = [e for e in events if isinstance(e, TickAdvanced)]
        assert len(tick_events) == 1
        assert tick_events[0].tick == 1

    def test_snapshot_reflects_current_tick(self) -> None:
        engine = _simple_engine()
        engine.advance_tick()
        engine.advance_tick()
        snap = engine.snapshot()
        assert snap.tick == 2

    def test_snapshot_width_height(self) -> None:
        engine = _simple_engine()
        snap = engine.snapshot()
        assert snap.width == 5
        assert snap.height == 5

    def test_world_accessible(self) -> None:
        engine = _simple_engine()
        assert engine.world.width == 5


class TestDeterminism:
    def test_same_seed_same_events(self) -> None:
        """Two engines with identical seeds produce identical event sequences."""
        engine_a = _simple_engine(seed=7)
        engine_b = _simple_engine(seed=7)
        events_a = [engine_a.advance_tick() for _ in range(5)]
        events_b = [engine_b.advance_tick() for _ in range(5)]
        assert events_a == events_b

    def test_different_seeds_different_random(self) -> None:
        """Engines with different seeds draw different random values."""
        engine_a = _simple_engine(seed=1)
        engine_b = _simple_engine(seed=2)
        # The internal Random state differs; draw a value from each.
        val_a = engine_a.random.random()
        val_b = engine_b.random.random()
        assert val_a != val_b
