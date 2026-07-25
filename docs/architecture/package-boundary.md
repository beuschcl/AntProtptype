# Package Boundary Overview

This document describes the responsibilities of each Python package and
the import rules that enforce separation of concerns.

---

## Package map

```
ant_colony/
├── domain/        ← Core domain model.  No dependencies outside stdlib.
├── simulation/    ← Engine layer.  Imports domain only.
└── scenario/      ← I/O adapter.  Imports domain + simulation.
```

---

## `ant_colony.domain`

**Responsibility**: Pure domain model – the language of the problem.

| Module | Contents |
|---|---|
| `coordinate` | `Coordinate` immutable value object |
| `terrain` | `TerrainType` enum |
| `world_objects` | `WorldObject`, `Obstacle`, `Resource`, `Nest` |
| `world` | `World` aggregate (grid, occupancy, queries, events) |
| `events` | Typed domain events |
| `snapshot` | `WorldSnapshot`, `ResourceSnapshot` |
| `errors` | Domain-specific exception hierarchy |

**Allowed imports**: Python stdlib only.  
**Forbidden imports**: `pygame`, `tkinter`, `curses`, any UI or network library.  
**Rule**: Nothing outside `ant_colony.domain` may be imported here.

---

## `ant_colony.simulation`

**Responsibility**: Drive the domain model forward in discrete time steps.

| Module | Contents |
|---|---|
| `engine` | `SimulationEngine` – fixed-tick loop, seeded `random.Random` |

**Allowed imports**: `ant_colony.domain`, Python stdlib.  
**Forbidden imports**: Presentation, I/O, scenario parsing.

---

## `ant_colony.scenario`

**Responsibility**: Load human-readable configuration files and construct
validated domain objects.  This is an *infrastructure adapter* – it reads
files, so it is intentionally separated from the domain.

| Module | Contents |
|---|---|
| `config` | Typed dataclass representations of a scenario file |
| `loader` | `ScenarioLoader` – TOML → `ScenarioConfig` → `World` + engine |

**Allowed imports**: `ant_colony.domain`, `ant_colony.simulation`, stdlib.  
**Forbidden imports**: Presentation packages.

---

## Dependency graph

```
scenario  ──→  simulation  ──→  domain
    │                              ↑
    └──────────────────────────────┘
```

All arrows point inward.  `domain` has no outward dependencies.

---

## Import rules (enforced by mypy)

1. `ant_colony.domain` imports only the stdlib.
2. `ant_colony.simulation` imports only `ant_colony.domain` and the stdlib.
3. `ant_colony.scenario` imports `ant_colony.domain`,
   `ant_colony.simulation`, and the stdlib.
4. Test modules may import anything.

---

## Future packages (not yet implemented)

| Package | Planned responsibility |
|---|---|
| `ant_colony.renderer` | PyGame / terminal renderer – reads `WorldSnapshot` only |
| `ant_colony.ant` | Ant agents, AI, pheromone decay – imports domain + simulation |
| `ant_colony.persistence` | Save / load world state |
