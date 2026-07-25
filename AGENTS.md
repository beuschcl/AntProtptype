# AGENTS.md – Architectural Constraints for All Agents

This file defines the durable constraints that every automated agent
(Copilot, CI bots, code-review tools, etc.) must respect when working in
this repository.  It mirrors the content of `.github/copilot-instructions.md`
and is the authoritative reference.

---

## Project scope (this PR / phase)

**In scope**

* Square-grid world with terrain, obstacles, resources, nest
* Deterministic fixed-tick simulation engine (seeded `random.Random`)
* TOML-based scenario loader
* Typed domain events
* Immutable world snapshots
* Pytest test suite (unit / integration / acceptance)
* GitHub Actions CI (lint, type-check, tests)

**Explicitly out of scope**

* Ants, ant AI, pathfinding, colony behaviour
* Pheromone trails
* PyGame or any graphical rendering
* Persistence (save/load game state)
* Networking

---

## Architectural constraints

| Constraint | Rule |
|---|---|
| Domain isolation | `ant_colony.domain` must not import any presentation, infrastructure, or I/O package. |
| Immutability | `Coordinate`, events, and `WorldSnapshot` are immutable value objects. |
| Determinism | All random decisions flow through `SimulationEngine.random` (seeded `random.Random`). |
| Snapshot safety | `World.take_snapshot()` returns copies of internal collections; callers cannot mutate live world state through snapshots. |
| No global state | Modules have no module-level mutable singletons. |
| Circular imports | Banned. Enforced by mypy strict mode and import order conventions. |
| `src/` layout | All importable code lives under `src/ant_colony/`. |
| Config | World construction is always driven by a scenario file; no hardcoded default worlds in application startup. |

---

## Decision log (see `docs/architecture/adr/`)

| ADR | Decision |
|---|---|
| 001 | Square grid (not hex or continuous) |
| 002 | Headless domain (no presentation coupling) |
| 003 | Fixed ticks (not event-driven or real-time) |
| 004 | Seeded `random.Random` (not `secrets` or external source) |
| 005 | TOML scenario files (stdlib `tomllib`) |
| 006 | `src/` layout for packaging hygiene |

---

## How to run locally

```bash
# Set up
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Demo
python -m ant_colony

# Tests
pytest

# Lint
ruff check src/ tests/
ruff format --check src/ tests/

# Type-check
mypy src/
```
