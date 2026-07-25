# Glossary

Terms used throughout the codebase and documentation.

---

## Core concepts

**Ant**
A simulated agent that moves through the world, collects resources, and
returns them to the nest.  *Not implemented in Phase 1.*

**Colony**
A group of ants sharing a single nest.  *Not implemented in Phase 1.*

**Coordinate**
An immutable integer `(x, y)` position on the square grid.  `x` is the
column (left→right, 0-based); `y` is the row (top→bottom, 0-based).

**Domain event**
An immutable, typed value object that describes a meaningful state change
in the world (e.g. `ResourceDepleted`, `TickAdvanced`).  Events are
emitted by the world and engine; they are never mutable.

**Grid**
The rectangular array of cells that defines the world.  Each cell has a
terrain type and may hold at most one solid world object.

**Nest**
The colony's home location.  A passive world object; ants start and
return here.  Only one nest per world.

**Obstacle**
An impassable world object (rock, boulder, etc.) that blocks movement
through its cell.

**Pheromone**
A chemical trail laid by ants to guide future ants.  *Not implemented in
Phase 1.*

**Resource**
A finite collectible deposit (food pile, etc.) placed at a grid cell.
Has a current `amount` and a `max_amount`.  Resources can be depleted
toward zero.

**Scenario**
A human-readable TOML configuration file that describes the world
geometry, object placement, and simulation parameters.  Scenario files
live in `scenarios/`.

**Seed**
An integer used to initialise `random.Random` inside `SimulationEngine`.
The same seed + scenario always produce the same simulation output.

**Simulation engine**
`SimulationEngine` – owns the world and advances it one tick at a time.
Holds the seeded `random.Random` instance.

**Snapshot** (`WorldSnapshot`)
An immutable, deep-enough copy of the world state at a specific tick.
Safe to pass to renderers or external observers without risking mutation
of the live world.

**Terrain**
The base layer of a grid cell.  `OPEN` cells allow movement; `WALL` cells
block movement and cannot hold world objects.

**Tick**
One discrete time-step in the simulation.  The engine advances the world
by exactly one tick per call to `SimulationEngine.advance_tick()`.

**Traversable**
A cell is traversable when its terrain is `OPEN` **and** it contains no
`Obstacle`.  Resources and the nest do not block traversal.

**World**
The mutable domain aggregate that owns the terrain grid, all world
objects, and the spatial state.  Only the simulation engine and the
scenario loader should mutate a world after construction.

**World object**
Any passive entity that occupies a grid cell: `Obstacle`, `Resource`, or
`Nest`.  World objects have no behaviour; they are operated on by the
world or future simulation components.
