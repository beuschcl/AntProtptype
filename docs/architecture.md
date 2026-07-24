
## `docs/architecture.md`

```markdown
# Architecture

## Purpose

The Ant Colony project models a colony as a collection of interacting objects rather than as one central simulation procedure.

The architecture is intended to support gradual addition of sensing, knowledge, food collection, colony growth, pheromones, and other emergent systems without replacing the core design.

## Package structure

### `ant_colony.entities`

Contains objects with identity and a position in the simulated world.

Current entities include:

- `Entity`
- `Ant`
- `Food`
- `Nest`

`Entity` provides shared identity and spatial properties. Specialized entities own their domain-specific state and behavior.

### `ant_colony.components`

Contains reusable capabilities that belong to entities through composition.

Current components include:

- Inventory
- Senses
- State

An ant contains these components rather than inheriting separate inventory, sensing, or state classes.

### `ant_colony.knowledge`

Contains the ant knowledge model.

This package will evolve to support object-based memories and operations such as:

```python
remember()
recall()
share_with()
count()