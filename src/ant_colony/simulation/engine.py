"""Fixed-tick deterministic simulation engine.

:class:`SimulationEngine` owns the mutable :class:`~ant_colony.domain.world.World`
and advances it one tick at a time.  Seeded randomness is injected so
that any simulation with the same seed and scenario always produces the
same sequence of events.

The engine itself does nothing during a tick except:

1. Emit a :class:`~ant_colony.domain.events.TickAdvanced` event.
2. Return the accumulated event list to callers.

Future behaviour (ant movement, pheromone decay, etc.) will be added as
*tick processors* that receive the engine's ``random`` instance and
return additional events.
"""

from __future__ import annotations

import random as _random
from typing import TYPE_CHECKING

from ant_colony.domain.events import AnyEvent, TickAdvanced
from ant_colony.domain.world import World

if TYPE_CHECKING:
    from ant_colony.domain.snapshot import WorldSnapshot


class SimulationEngine:
    """Drives the simulation forward one tick at a time.

    Args:
        world:  The :class:`~ant_colony.domain.world.World` to simulate.
                The engine takes ownership; callers should not mutate
                the world directly after handing it to the engine.
        seed:   Integer seed for the internal :class:`random.Random`
                instance.  The same *seed* always produces the same
                sequence of random decisions.

    Example::

        engine = SimulationEngine(world=my_world, seed=42)
        events = engine.advance_tick()
    """

    def __init__(self, world: World, seed: int) -> None:
        self._world = world
        self._random = _random.Random(seed)
        self._tick = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def tick(self) -> int:
        """Current tick number (0 before first advance)."""
        return self._tick

    @property
    def world(self) -> World:
        """The underlying mutable world.

        Prefer using :meth:`snapshot` for read-only access.
        """
        return self._world

    @property
    def random(self) -> _random.Random:
        """The seeded :class:`random.Random` instance.

        Future tick processors receive this instance so that all random
        decisions flow through a single, reproducible stream.
        """
        return self._random

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def advance_tick(self) -> list[AnyEvent]:
        """Advance the simulation by one tick.

        Returns:
            An ordered list of :data:`~ant_colony.domain.events.AnyEvent`
            objects describing everything that changed during this tick.
        """
        self._tick += 1
        events: list[AnyEvent] = [TickAdvanced(tick=self._tick)]
        # Future tick processors will append their events here.
        return events

    def snapshot(self) -> WorldSnapshot:
        """Return an immutable snapshot of the current world state."""
        return self._world.take_snapshot(tick=self._tick)

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"SimulationEngine(tick={self._tick}, world={self._world!r}, seed=<hidden>)"
