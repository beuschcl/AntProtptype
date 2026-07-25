"""Vertical slice demonstration – headless ant-colony simulation.

Run with::

    python -m ant_colony [path/to/scenario.toml]

Demonstrates:
1. Loading an example scenario from TOML.
2. Constructing and validating the world.
3. Advancing through several deterministic ticks.
4. Depleting a resource via an explicit world operation.
5. Printing a text snapshot proving the simulation runs headlessly.

The output is deterministic: the same scenario file and seed always
produce identical snapshots and event logs.
"""

from __future__ import annotations

import sys
from pathlib import Path

from ant_colony.domain.events import ResourceDepleted, ResourceExhausted, TickAdvanced
from ant_colony.scenario.loader import ScenarioLoader


def _event_label(event: object) -> str:
    if isinstance(event, TickAdvanced):
        return f"  [tick]      Tick {event.tick}"
    if isinstance(event, ResourceDepleted):
        coord = event.coordinate
        return (
            f"  [resource]  ({coord.x},{coord.y}) depleted by "
            f"{event.amount_depleted}, remaining={event.remaining}"
        )
    if isinstance(event, ResourceExhausted):
        coord = event.coordinate
        return f"  [resource]  ({coord.x},{coord.y}) EXHAUSTED"
    return f"  [event]     {event!r}"


def main(scenario_path: str | Path | None = None) -> None:
    """Run the demonstration."""
    if scenario_path is None:
        # Default: scenarios/example.toml relative to the project root.
        here = Path(__file__).parent
        scenario_path = here.parent.parent / "scenarios" / "example.toml"
        if not scenario_path.exists():
            # Installed package fallback: look next to the current working dir
            scenario_path = Path("scenarios") / "example.toml"

    print("=" * 60)
    print("  AntColony – headless simulation demo")
    print("=" * 60)
    print(f"\nLoading scenario: {scenario_path}\n")

    config, engine = ScenarioLoader.load_file(scenario_path)

    print(f"Scenario : {config.name}")
    print(f"World    : {engine.world.width}×{engine.world.height} grid")
    print(f"Seed     : {config.simulation.seed}")
    print(f"Ticks    : {config.simulation.ticks}")
    print()

    # ----------------------------------------------------------------
    # Initial snapshot
    # ----------------------------------------------------------------
    snap0 = engine.snapshot()
    print("--- Initial world state (tick 0) ---")
    print(snap0.to_text_grid())
    print()

    # ----------------------------------------------------------------
    # Advance through configured number of ticks
    # ----------------------------------------------------------------
    all_events: list[object] = []
    for _ in range(config.simulation.ticks):
        events = engine.advance_tick()
        all_events.extend(events)

    print(f"--- After {engine.tick} tick(s) ---")
    print(engine.snapshot().to_text_grid())
    print()

    # ----------------------------------------------------------------
    # Manually deplete a resource (vertical-slice requirement #4)
    # ----------------------------------------------------------------
    # Find the first non-exhausted resource in the snapshot.
    snap = engine.snapshot()
    active = [r for r in snap.resources if not r.is_exhausted]
    if active:
        target = active[0]
        print(
            f"Depleting resource at ({target.coordinate.x},{target.coordinate.y}) "
            f"by {target.amount} (full depletion)..."
        )
        depletion_events = engine.world.deplete_resource(target.coordinate, target.amount)
        all_events.extend(depletion_events)
        print("Done.\n")
    else:
        print("No active resources to deplete.\n")

    # ----------------------------------------------------------------
    # Final snapshot
    # ----------------------------------------------------------------
    snap_final = engine.snapshot()
    print("--- Final world state ---")
    print(snap_final.to_text_grid())
    print()

    # ----------------------------------------------------------------
    # Event log
    # ----------------------------------------------------------------
    print(f"--- Event log ({len(all_events)} event(s)) ---")
    for ev in all_events:
        print(_event_label(ev))
    print()

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    remaining = sum(r.amount for r in snap_final.resources)
    print(f"Total resources remaining : {remaining}")
    print(f"Simulation ticks elapsed  : {engine.tick}")
    print("\nDone – simulation ran headlessly (no graphics required).")


if __name__ == "__main__":
    path_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(path_arg)
