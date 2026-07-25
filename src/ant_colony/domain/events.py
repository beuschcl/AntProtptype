"""Typed domain events emitted during simulation.

Events are immutable value objects that describe meaningful state changes
in the world.  They carry only the data needed by observers; they do not
embed mutable references.

All events inherit from :class:`WorldEvent` so callers can narrow types
with ``isinstance`` checks or a ``match`` statement.
"""

from __future__ import annotations

import dataclasses

from ant_colony.domain.coordinate import Coordinate


@dataclasses.dataclass(frozen=True)
class WorldEvent:
    """Base class for all world events.  Never instantiated directly."""


@dataclasses.dataclass(frozen=True)
class TickAdvanced(WorldEvent):
    """Emitted at the start of each simulation tick.

    Attributes:
        tick: The new tick number (1-based).
    """

    tick: int


@dataclasses.dataclass(frozen=True)
class ResourceDepleted(WorldEvent):
    """Emitted when a resource deposit loses some quantity.

    Attributes:
        coordinate:       Grid location of the resource.
        amount_depleted:  Quantity removed in this operation.
        remaining:        Quantity still available after depletion.
    """

    coordinate: Coordinate
    amount_depleted: int
    remaining: int


@dataclasses.dataclass(frozen=True)
class ResourceExhausted(WorldEvent):
    """Emitted when a resource deposit reaches zero quantity.

    Attributes:
        coordinate: Grid location of the now-exhausted resource.
    """

    coordinate: Coordinate


# Discriminated union of all concrete event types.
AnyEvent = TickAdvanced | ResourceDepleted | ResourceExhausted
