# Ant Colony

A Python simulation exploring how individual ants, local knowledge, environmental sensing, and simple behaviors can produce colony-level activity.

The project is also being used as a structured Python learning project focused on maintainable architecture, object-oriented design, testing, and iterative development.

## Current capabilities

- Pygame simulation window
- Food-only colony loop: ants scout, collect food, return to nest, nest spends
  food on energy upkeep, colony grows to 50 ants
- Ant entities with randomized movement
- Nest and food entities (no water or building-material simulation resources)
- Ant selection with a mouse click
- Inspector panel for selected ants
- Camera abstraction
- Entity shape primitives
- Basic ant inventory, senses, state, and knowledge components

## Planned capabilities

- Environmental sensing
- Food discovery
- Food collection and delivery
- Nest inventory
- Ant spawning
- Knowledge sharing
- Pheromone trails
- Emergent colony behavior

## Requirements

- Python 3.12 or newer
- Pygame

## Installation

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1