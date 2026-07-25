# ADR 003 – Fixed Ticks (not event-driven or real-time)

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

Simulation time can advance in several ways:

1. **Fixed ticks** – the simulation advances by one discrete step per
   call; the caller controls wall-clock timing.
2. **Variable ticks** – steps have variable logical duration.
3. **Event-driven** – the simulation jumps to the next scheduled event.
4. **Real-time** – physical time drives the simulation.

## Decision

Use **fixed ticks**: `SimulationEngine.advance_tick()` advances the world
by exactly one logical time unit.

## Rationale

* Simplest mental model: the world changes exactly once per tick.
* Determinism is trivially guaranteed: tick N is always the same given
  the same seed and prior ticks.
* Replay is simple: re-run from tick 0 with the same seed.
* The caller (renderer, test, CLI) decides how often to call
  `advance_tick()` and at what wall-clock rate.
* Event-driven simulation would complicate the current domain without
  clear benefit.

## Consequences

* `SimulationEngine.tick` counts elapsed ticks.
* A `TickAdvanced` event is emitted at the start of every tick.
* Future *tick processors* (ant movement, pheromone decay) will be called
  inside `advance_tick()` and will append their events to its return list.
* The simulation has no real-time dependency; tests run as fast as
  possible.
