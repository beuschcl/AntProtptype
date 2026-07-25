# ADR 004 – Seeded `random.Random` for Determinism

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

The simulation will involve probabilistic decisions (ant direction choice,
pheromone noise, etc.).  Options:

1. **Global `random` module** – simple but non-deterministic across calls
   and untestable.
2. **`secrets` module** – cryptographically random; not repeatable.
3. **Per-engine `random.Random` instance** – seeded, fully reproducible.
4. **External PRNG library** (NumPy, etc.) – heavier dependency.

## Decision

Use a single **`random.Random` instance seeded in `SimulationEngine`**.
All random decisions in the simulation must go through
`SimulationEngine.random`.

## Rationale

* `random.Random` is stdlib; no extra dependency.
* A seeded instance is fully reproducible: same seed + same inputs →
  same outputs, forever.
* Injecting the instance via `engine.random` avoids global state and
  makes the randomness source explicit.
* Tests can pass a fixed seed and assert exact outcomes.
* Replay is straightforward: store the seed in the scenario file.

## Consequences

* Future tick processors must accept or retrieve `engine.random` – they
  must not call `random.random()` directly.
* The seed is stored in the scenario TOML under `[simulation] seed`.
* `SimulationEngine.__repr__` deliberately hides the seed value to avoid
  accidental logging.
