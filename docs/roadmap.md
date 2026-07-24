
---

## `docs/roadmap.md`

```markdown
# Roadmap

## Completed foundation

- Core simulation package
- World object
- Ant, food, and nest entities
- Ant movement and state
- Entity structure
- Ant selection
- Inspector panel
- Graphics primitives
- Camera abstraction
- Initial repository documentation and packaging

## Milestone 2 — Rendering boundary

### Goal

Complete the separation between simulation objects and Pygame rendering.

### Work

- Remove Pygame imports from entities and world logic
- Make entities expose immutable shape descriptions
- Make the renderer draw all supported shapes
- Remove duplicate drawing paths
- Define selection-ring rendering in the UI layer
- Use world dimensions instead of full screen dimensions for ant movement

### Exit criteria

- Pygame is limited to application and graphics/UI packages
- `World` contains no drawing method
- Entities contain no direct Pygame drawing calls
- The application remains visually equivalent

## Milestone 3 — Entity collection

### Goal

Give the world one consistent entity model.

### Work

- Introduce `world.entities`
- Support filtered access to ants, food, and nests
- Add explicit entity registration and removal methods
- Preserve selected-ant behavior

### Exit criteria

- World-level systems can iterate over all entities
- Entity removal is controlled through world methods
- Existing simulation behavior remains intact

## Milestone 4 — Knowledge system

### Goal

Create an object-based memory system owned by each ant.

### Work

- Define memory objects
- Implement `remember`
- Implement `recall`
- Implement `count`
- Implement `share_with`
- Prevent uncontrolled duplicate memories
- Add unit tests

### Exit criteria

- Ants can retain knowledge of discovered entities
- Memories can be queried by type or subject
- Knowledge can be shared between ants

## Milestone 5 — Sensing and discovery

### Goal

Allow ants to discover nearby entities.

### Interaction rule

An entity is detectable when the distance between it and the ant is less than the combined sensing and discoverability radii.

```text
distance < ant sensing radius + entity discoverable radius