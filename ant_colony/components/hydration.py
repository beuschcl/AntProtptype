class HydrationNeed:
    """Bounded hydration need for an ant."""

    def __init__(self, maximum: float) -> None:
        if maximum < 0:
            raise ValueError("maximum must be non-negative")
        self._maximum = maximum
        self._current = maximum

    @property
    def current(self) -> float:
        return self._current

    @property
    def maximum(self) -> float:
        return self._maximum

    def decay(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("decay amount must be non-negative")
        self._current = max(
            0.0,
            self._current - amount,
        )

    def restore(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("restore amount must be non-negative")
        self._current = min(
            self._maximum,
            self._current + amount,
        )
