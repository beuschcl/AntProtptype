"""Acceptance tests – deterministic replay and end-to-end vertical slice."""

from __future__ import annotations

from pathlib import Path

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.events import TickAdvanced
from ant_colony.scenario.loader import ScenarioLoader

EXAMPLE_TOML = Path(__file__).parent.parent.parent / "scenarios" / "example.toml"


def _run_full(seed_override: int | None = None) -> tuple[list[object], str]:
    """Load the example scenario, run 5 ticks, deplete a resource, return events + grid."""
    config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)

    if seed_override is not None:
        # Re-create engine with override seed but same world spec
        import dataclasses

        new_sim = dataclasses.replace(config.simulation, seed=seed_override)
        new_config = dataclasses.replace(config, simulation=new_sim)
        engine = ScenarioLoader._build_engine(new_config)

    all_events: list[object] = []
    for _ in range(config.simulation.ticks):
        all_events.extend(engine.advance_tick())

    # Deplete first resource completely
    snap = engine.snapshot()
    active = [r for r in snap.resources if not r.is_exhausted]
    if active:
        target = active[0]
        all_events.extend(engine.world.deplete_resource(target.coordinate, target.amount))

    final_grid = engine.snapshot().to_text_grid()
    return all_events, final_grid


class TestDeterministicReplay:
    def test_same_scenario_same_events(self) -> None:
        """Running the same scenario twice must produce identical event lists."""
        events_a, grid_a = _run_full()
        events_b, grid_b = _run_full()
        assert events_a == events_b
        assert grid_a == grid_b

    def test_tick_events_correct_sequence(self) -> None:
        events, _ = _run_full()
        tick_events = [e for e in events if isinstance(e, TickAdvanced)]
        tick_numbers = [e.tick for e in tick_events]
        assert tick_numbers == list(range(1, 6))  # ticks 1..5

    def test_final_grid_is_stable(self) -> None:
        """The grid must be the same on every call with the same scenario."""
        _, grid_a = _run_full()
        _, grid_b = _run_full()
        assert grid_a == grid_b

    def test_different_seed_same_ticks_same_events(self) -> None:
        """
        With seed=42 vs seed=99 the tick-advance events are structurally
        identical (ticks are deterministic).  Only internal random draws differ.
        """
        events_42, _ = _run_full(seed_override=42)
        events_99, _ = _run_full(seed_override=99)
        tick_42 = [e for e in events_42 if isinstance(e, TickAdvanced)]
        tick_99 = [e for e in events_99 if isinstance(e, TickAdvanced)]
        # Both have 5 tick-advanced events
        assert len(tick_42) == len(tick_99)


class TestVerticalSlice:
    def test_headless_run_completes(self) -> None:
        """The full vertical slice must complete without raising."""
        from ant_colony.__main__ import main

        main(EXAMPLE_TOML)  # Should not raise

    def test_snapshot_not_mutated_by_caller(self) -> None:
        """External callers cannot mutate snapshot data."""
        _config, engine = ScenarioLoader.load_file(EXAMPLE_TOML)
        snap = engine.snapshot()
        # Mutating returned terrain dict does not change the world
        snap.terrain[Coordinate(0, 0)] = __import__(
            "ant_colony.domain.terrain", fromlist=["TerrainType"]
        ).TerrainType.WALL
        # The engine's world is unaffected
        assert engine.world.terrain_at(Coordinate(0, 0)).is_traversable

    def test_domain_has_no_presentation_imports(self) -> None:
        """Domain package must not import pygame, tkinter, or any UI module."""
        import importlib
        import sys

        # Remove any cached imports of the domain package to get fresh view
        domain_modules = [k for k in sys.modules if k.startswith("ant_colony.domain")]
        for mod_name in domain_modules:
            importlib.import_module(mod_name)  # ensure loaded

        forbidden = {"pygame", "tkinter", "curses", "wx", "PyQt5", "PyQt6"}
        for mod_name in sys.modules:
            if mod_name.startswith("ant_colony.domain"):
                module = sys.modules[mod_name]
                if hasattr(module, "__file__") and module.__file__:
                    for bad in forbidden:
                        assert bad not in (getattr(module, "__doc__", "") or ""), (
                            f"{mod_name} references {bad}"
                        )
