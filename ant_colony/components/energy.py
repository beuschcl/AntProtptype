class EnergyNeed:
    """Bounded energy for an ant.

    ``spend`` returns ``False`` without modifying state when the current
    level is insufficient; all other arithmetic is validated against
    negative inputs.
    """

    def __init__(self, maximum: int) -> None:
        if maximum < 0:
            raise ValueError("maximum must be non-negative")
        self._maximum = maximum
        self._current = maximum

    @property
    def current(self) -> int:
        return self._current

    @property
    def maximum(self) -> int:
        return self._maximum

    @property
    def is_full(self) -> bool:
        return self._current == self._maximum

    def spend(self, amount: int) -> bool:
        """Deduct *amount* from current energy.

        Returns ``True`` and applies the deduction if current >= amount.
        Returns ``False`` (no-op) if current < amount.
        Raises ``ValueError`` for negative *amount*.
        """
        if amount < 0:
            raise ValueError("spend amount must be non-negative")
        if self._current < amount:
            return False
        self._current -= amount
        return True

    def restore(self, amount: int) -> None:
        """Add *amount* to current energy, capped at maximum.

        Raises ``ValueError`` for negative *amount*.
        """
        if amount < 0:
            raise ValueError("restore amount must be non-negative")
        self._current = min(self._maximum, self._current + amount)
