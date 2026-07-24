
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
- Rendering boundary
- Unified world entity collection
- Controlled entity registration and removal
- Read-only filtered entity views

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