
---

## `docs/adr/0001-project-architecture.md`

```markdown
# ADR 0001: Use object-oriented, component-based simulation architecture

- Status: Accepted
- Date: 2026-07-24

## Context

The simulation will grow beyond simple ant movement to include sensing, memories, food collection, nest inventory, colony growth, pheromones, and emergent behavior.

A procedural design or one central simulation class would become increasingly difficult to maintain as these systems are added.

The project is also intended to teach sustainable Python engineering practices. The architecture therefore needs to make ownership of state and behavior explicit.

## Decision

The simulation will use an object-oriented architecture with composition as the primary mechanism for assembling behavior.

Important domain concepts will be represented as objects, including:

- Ants
- Food
- Nests
- Memories
- Inventory
- Senses
- Rendering shapes

Entities will own their state and behavior.

Reusable capabilities such as inventory, senses, and knowledge will be composed into entities rather than implemented through deep inheritance hierarchies.

The world will coordinate entities and world-level interactions, but behavior that naturally belongs to an entity or component will remain with that object.

Rendering will be separated from simulation behavior. Entities will expose render-neutral shape descriptions, and the renderer will translate those descriptions into Pygame calls.

## Consequences

### Positive

- Responsibilities are easier to identify.
- New entity and behavior types can be added incrementally.
- Simulation rules can be tested without opening a Pygame window.
- Components can evolve independently.
- Pygame remains an implementation detail rather than a domain dependency.
- The design supports future systems without requiring a central rewrite.

### Negative

- The project contains more files and classes than a small procedural prototype.
- Object boundaries require deliberate design.
- Some interactions may require coordination between several objects.
- Transitional refactoring is required because some current rendering code still depends directly on Pygame.

## Alternatives considered

### Single simulation class

Rejected because it would concentrate entity storage, behavior, rendering, input handling, and interaction rules in one class.

### Pure inheritance hierarchy

Rejected because inventory, senses, and knowledge are capabilities rather than entity identities. Composition allows these capabilities to evolve without creating rigid inheritance trees.

### Entity-component-system framework

Deferred. A full ECS would add significant abstraction before the simulation requires it. The current component-based object model provides sufficient extensibility with less complexity.

## Implementation guidance

- Add abstractions only when they support a current milestone.
- Keep public methods explicit.
- Avoid direct modification of another object's private state.
- Keep the application runnable after every milestone.
- Record significant architectural changes in additional ADRs.