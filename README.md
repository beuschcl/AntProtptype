# AntColony

> Creating a silly game where you set up the environment and see how the ants react.

This repository contains the **world-only foundation** for an observable,
headless ant-colony simulation written in Python.  The current phase delivers
a clean domain model, a deterministic simulation engine, and a scenario loader
– no ants, no graphics, no PyGame yet.

---

## Quick start

```bash
# 1. Clone and enter the repo
git clone https://github.com/beuschcl/AntColony.git
cd AntColony

# 2. Create and activate a virtual environment
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Run the headless demo
python -m ant_colony
# or point at your own scenario file:
python -m ant_colony scenarios/example.toml
```

---

## PyCharm setup

1. Open the project root in PyCharm.
2. **File → Settings → Project → Python Interpreter → Add Interpreter →
   Add Local Interpreter → Virtualenv Environment → Existing**.
3. Point to `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows).
4. Mark `src/` as a **Sources Root** (right-click → *Mark Directory as →
   Sources Root*) so imports resolve correctly in the IDE.
5. Install plugins: *Ruff* (for linting) and *mypy* (for type-checking).

---

## Common commands

| Task | Command |
|---|---|
| Run demo | `python -m ant_colony` |
| Run all tests | `pytest` |
| Run unit tests only | `pytest tests/unit/` |
| Run with coverage | `pytest --cov=ant_colony --cov-report=term-missing` |
| Lint | `ruff check src/ tests/` |
| Auto-fix lint | `ruff check --fix src/ tests/` |
| Format check | `ruff format --check src/ tests/` |
| Auto-format | `ruff format src/ tests/` |
| Type-check | `mypy src/` |

---

## Project layout

```
src/ant_colony/
    __init__.py         Package version
    __main__.py         Headless demo (python -m ant_colony)
    domain/             Pure domain model
        coordinate.py   Immutable (x, y) grid position
        terrain.py      TerrainType enum (OPEN / WALL)
        world_objects.py Obstacle, Resource, Nest
        world.py        World aggregate (grid, occupancy, queries)
        events.py       Typed domain events
        snapshot.py     Immutable WorldSnapshot
        errors.py       Domain-specific exceptions
    simulation/
        engine.py       SimulationEngine (fixed-tick, seeded)
    scenario/
        config.py       Typed scenario configuration (dataclasses)
        loader.py       TOML scenario loader → World + engine

tests/
    unit/               Fast, pure-unit tests
    integration/        Tests that load scenario files from disk
    acceptance/         End-to-end determinism proofs

scenarios/
    example.toml        Runnable "Small Valley" example scenario

docs/architecture/      Architecture documentation and ADRs
```

---

## Architecture overview

The domain layer (`ant_colony.domain`) is completely independent of
graphics, I/O, and any future ant AI.  All simulation state flows through
`SimulationEngine`, which holds a seeded `random.Random` and a mutable
`World`.  Read-only observers receive `WorldSnapshot` instances that cannot
mutate the live world.

See `docs/architecture/` for the full charter, glossary, package-boundary
diagram, and ADRs.

---

## Scenario format

Scenarios are plain TOML files.  See `scenarios/example.toml` for a
fully-commented example.

```toml
name = "My Scenario"

[world]
width  = 20
height = 20
walls  = [[5, 0], [5, 1]]   # [x, y] pairs

[[world.obstacles]]
x = 3
y = 4

[[world.resources]]
x = 10
y = 10
amount     = 100
max_amount = 100

[world.nest]
x = 1
y = 1

[simulation]
seed  = 42
ticks = 5
```

---

## Contributing

* Read `AGENTS.md` for the hard architectural rules before opening a PR.
* Run `pytest && ruff check src/ tests/ && mypy src/` before pushing.
* Write or update an ADR in `docs/architecture/adr/` for any non-trivial
  design decision.
