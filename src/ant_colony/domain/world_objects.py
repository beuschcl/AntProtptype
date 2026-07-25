"""World objects that occupy grid cells.

A *world object* is a passive entity that exists at a specific coordinate.
World objects have no behaviour of their own; they are operated on by the
``World`` or by future simulation components.

Class hierarchy (shallow – composition is preferred):

    WorldObject          abstract base
    ├── Obstacle         blocks traversal
    ├── Resource         collectible deposit with finite amount
    └── Nest             passive colony origin marker
"""

from __future__ import annotations

import abc
from typing import final


class WorldObject(abc.ABC):
    """Abstract base for every object that can occupy a grid cell."""

    @property
    @abc.abstractmethod
    def blocks_traversal(self) -> bool:
        """Return ``True`` if this object prevents movement through its cell."""

    @property
    @abc.abstractmethod
    def kind(self) -> str:
        """Human-readable type label used in error messages and snapshots."""


@final
class Obstacle(WorldObject):
    """An impassable terrain feature (rock, wall segment, etc.).

    Obstacles are immutable – once placed they cannot be modified.
    """

    @property
    def blocks_traversal(self) -> bool:
        return True

    @property
    def kind(self) -> str:
        return "obstacle"

    def __repr__(self) -> str:
        return "Obstacle()"


@final
class Resource(WorldObject):
    """A finite deposit that can be collected (depleted) by ants.

    Args:
        amount:     Initial quantity available.
        max_amount: Maximum capacity; defaults to *amount*.

    Raises:
        ValueError: If *amount* or *max_amount* are non-positive or
                    *amount* > *max_amount*.
    """

    def __init__(self, amount: int, max_amount: int | None = None) -> None:
        if amount <= 0:
            raise ValueError(f"Resource amount must be positive, got {amount}")
        resolved_max = amount if max_amount is None else max_amount
        if resolved_max <= 0:
            raise ValueError(f"Resource max_amount must be positive, got {resolved_max}")
        if amount > resolved_max:
            raise ValueError(
                f"Resource amount ({amount}) cannot exceed max_amount ({resolved_max})"
            )
        self._amount = amount
        self._max_amount = resolved_max

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def amount(self) -> int:
        """Current remaining quantity."""
        return self._amount

    @property
    def max_amount(self) -> int:
        """Maximum capacity of this deposit."""
        return self._max_amount

    @property
    def is_exhausted(self) -> bool:
        """Return ``True`` when no quantity remains."""
        return self._amount == 0

    # ------------------------------------------------------------------
    # Mutation (package-private; only ``World`` should call these)
    # ------------------------------------------------------------------

    def _deplete(self, amount: int) -> int:
        """Remove up to *amount* from the deposit.

        Returns the quantity actually removed.  Never goes negative.
        """
        if amount <= 0:
            raise ValueError(f"Deplete amount must be positive, got {amount}")
        removed = min(amount, self._amount)
        self._amount -= removed
        return removed

    # ------------------------------------------------------------------
    # WorldObject interface
    # ------------------------------------------------------------------

    @property
    def blocks_traversal(self) -> bool:
        return False

    @property
    def kind(self) -> str:
        return "resource"

    def __repr__(self) -> str:
        return f"Resource(amount={self._amount}, max_amount={self._max_amount})"


@final
class Nest(WorldObject):
    """The colony's home location.

    The nest is a passive marker; it does not block movement and has no
    state beyond its existence.  Only one nest may exist per world.
    """

    @property
    def blocks_traversal(self) -> bool:
        return False

    @property
    def kind(self) -> str:
        return "nest"

    def __repr__(self) -> str:
        return "Nest()"
