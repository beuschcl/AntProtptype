# Project Charter and Scope

## Purpose

AntColony is an observable, deterministic ant-colony simulation built in
Python.  The project exists to explore emergent collective behaviour: given
a configured environment, how do ant colonies discover resources, establish
trails, and adapt to obstacles?

## Vision

A fully interactive simulation where users configure terrain, obstacles,
and resource placement via a human-readable file, observe the colony
evolve in real time through a graphical renderer, and replay any run
deterministically from a seed.

## Phase 1 scope (this pull request)

Phase 1 delivers the **world-only foundation**.  It provides the stable
core on which ants, AI, and rendering will be built.

**In scope for Phase 1**

| Component | Description |
|---|---|
| Domain model | Immutable coordinates, terrain types, world objects (obstacle, resource, nest) |
| World aggregate | Bounded square grid, occupancy, traversability, neighbourhood queries |
| Domain events | Typed, immutable events for meaningful state changes |
| World snapshot | Immutable read-only view safe for future renderers |
| Simulation engine | Fixed-tick loop with seeded `random.Random` |
| Scenario loader | TOML config → validated World + engine |
| Test suite | Unit, integration, and acceptance tests |
| CI | GitHub Actions: lint (Ruff), type-check (mypy), tests (pytest) |
| Documentation | This charter, glossary, package boundaries, six ADRs |

**Explicitly deferred**

* Ants, ant AI, pathfinding, pheromone trails
* Colony behaviour (foraging, trail reinforcement)
* PyGame rendering or any graphical output
* Persistence (save / load)
* Networking or multiplayer
* Hex grids, continuous-space, or 3-D worlds

## Success criteria for Phase 1

1. Same scenario + seed → identical snapshots and events (determinism).
2. Invalid inputs raise clear domain-specific errors.
3. Domain code imports no presentation or infrastructure package.
4. External callers cannot mutate snapshots or internal world collections.
5. All tests, lint, and type checks pass in CI.
6. A single command (`python -m ant_colony`) runs the headless demo.

## Stakeholders

| Role | Person |
|---|---|
| Owner / game designer | @beuschcl |
| Automated implementer | GitHub Copilot Coding Agent |
