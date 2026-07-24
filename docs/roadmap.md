
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
- Immutable memory value objects
- Encapsulated ant knowledge store
- Knowledge recall and replacement
- Knowledge sharing between ants
- Configurable ant sensing component
- Entity detection using overlapping discovery radii
- Immutable entity observations
- Automatic discovery during world updates
- Ant knowledge populated from sensed entities
- Typed, capacity-limited ant inventory
- Immutable collected food portions
- Food quantity and depletion behavior
- Food target selection
- Directed movement toward food
- Proximity-based food collection
- Automatic removal of depleted food

## Milestone 7 — Return food to the nest

### Objective

Allow ants carrying food to return it to the colony.

### Planned capabilities

- Select the nest as a return target
- Move carrying ants toward the nest
- Deposit inventory contents at the nest
- Track colony food reserves
- Resume wandering after delivery
- Preserve discovered food knowledge for later use