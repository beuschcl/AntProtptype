# Copilot Coding Agent – Instructions

This file is read by GitHub Copilot Coding Agent before it begins any
task in this repository.  It establishes the non-negotiable architectural
constraints so that every generated change is consistent.

---

## Repository purpose

An observable, headless ant-colony simulation.  The current scope is the
**world foundation only** (grid, terrain, objects, events, deterministic
ticks, scenario loading).  Ants, AI, pathfinding, and graphics are
explicitly out of scope for this phase.

---

## Package layout

```
src/ant_colony/
    domain/       Pure domain model – no I/O, no graphics
    simulation/   SimulationEngine (fixed-tick, seeded)
    scenario/     TOML scenario loader
tests/
    unit/         Pure-unit tests (no I/O)
    integration/  Tests that touch the filesystem (scenarios/)
    acceptance/   End-to-end / determinism proofs
scenarios/        Human-readable TOML scenario files
docs/architecture/ Architecture docs and ADRs
```

---

## Hard rules (never violate)

1. **Domain code (`ant_colony.domain`) must never import** pygame, tkinter,
   curses, or any UI/presentation package.
2. **No global mutable state** – every module must be importable without
   side-effects.
3. **Circular imports are banned** – enforce with mypy's strict mode.
4. **`WorldSnapshot` is immutable** – external callers get copies, not
   references to live collections.
5. **Seeded determinism** – the `SimulationEngine` owns a single
   `random.Random` instance; nothing else uses `random` directly.
6. **`src/` layout** – all importable code lives under `src/`.
7. **No speculative abstractions** – only build what the current requirements
   need.  Document deferred decisions in ADRs.

---

## Coding standards

* Python ≥ 3.11; use `tomllib` (stdlib) for TOML parsing.
* Strict mypy (`strict = true` in `pyproject.toml`).
* Ruff for linting and formatting (line length 100).
* Prefer `dataclasses.dataclass(frozen=True)` for value objects and events.
* Prefer `enum.Enum` for domain enumerations.
* Small, focused classes; composition over inheritance.
* All public functions, methods, and classes must have docstrings and type
  annotations.

---

## Test requirements

* All tests must pass before merging.
* Every new public API must have at least one unit test.
* Acceptance tests must prove deterministic replay.
* Tests must not import presentation or infrastructure packages.

---

## Adding new features

1. Check existing ADRs in `docs/architecture/adr/`.
2. If a decision is new, write a brief ADR first.
3. Write failing tests before implementation.
4. Keep domain and simulation logic completely independent of I/O.
