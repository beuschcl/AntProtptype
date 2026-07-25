# ADR 001 – Use a Square Grid (not hex or continuous space)

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

The simulation needs a spatial model.  Common options:

1. **Square grid** – integer (x, y) coordinates, 4 or 8 neighbours.
2. **Hex grid** – equidistant 6 neighbours, popular in strategy games.
3. **Continuous 2-D space** – floating-point positions, arbitrary movement.

## Decision

Use a **square grid with integer coordinates**.

## Rationale

* Simplest model to implement and reason about.
* Integer coordinates make equality, hashing, and set membership trivial.
* 4-connected and 8-connected neighbourhood queries are standard.
* Easy to render as a grid of pixels or ASCII characters.
* Sufficient for the emergent-trail behaviour the game targets.
* Hex grids would require a non-trivial coordinate system (axial, offset,
  or cube) with no clear benefit at this stage.
* Continuous space would complicate collision detection, occupancy
  tracking, and determinism.

## Consequences

* Diagonal movement is optional (controlled by `include_diagonals=True`).
* Movement distance is measured in Manhattan distance or Chebyshev
  distance depending on connectivity choice.
* Future hex or continuous support would require a new spatial model, but
  this can be added behind a new `Coordinate` protocol without changing
  domain logic.
