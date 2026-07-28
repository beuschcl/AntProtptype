class HydrationNeed:
    """Bounded hydration need for an ant."""

    def __init__(self, maximum: float) -> None:
        self._maximum = maximum
        self._current = maximum

    @property
    def current(self) -> float:
        return self._current

    @property
    def maximum(self) -> float:
        return self._maximum

    def decay(self, amount: float) -> None:
        self._current = max(
            0.0,
            self._current - amount,
        )

    def restore(self, amount: float) -> None:
        self._current = min(
            self._maximum,
            self._current + amount,
        )
