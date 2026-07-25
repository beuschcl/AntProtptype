"""Unit tests for domain events."""

from __future__ import annotations

import pytest

from ant_colony.domain.coordinate import Coordinate
from ant_colony.domain.events import (
    ResourceDepleted,
    ResourceExhausted,
    TickAdvanced,
)


class TestTickAdvanced:
    def test_stores_tick(self) -> None:
        e = TickAdvanced(tick=5)
        assert e.tick == 5

    def test_is_frozen(self) -> None:
        e = TickAdvanced(tick=1)
        with pytest.raises((AttributeError, TypeError)):
            e.tick = 99  # type: ignore[misc]

    def test_equality(self) -> None:
        assert TickAdvanced(tick=3) == TickAdvanced(tick=3)
        assert TickAdvanced(tick=3) != TickAdvanced(tick=4)

    def test_hashable(self) -> None:
        s = {TickAdvanced(tick=1), TickAdvanced(tick=1)}
        assert len(s) == 1


class TestResourceDepleted:
    def test_stores_fields(self) -> None:
        coord = Coordinate(3, 4)
        e = ResourceDepleted(coordinate=coord, amount_depleted=10, remaining=40)
        assert e.coordinate == coord
        assert e.amount_depleted == 10
        assert e.remaining == 40

    def test_is_frozen(self) -> None:
        e = ResourceDepleted(coordinate=Coordinate(0, 0), amount_depleted=1, remaining=9)
        with pytest.raises((AttributeError, TypeError)):
            e.remaining = 99  # type: ignore[misc]


class TestResourceExhausted:
    def test_stores_coordinate(self) -> None:
        coord = Coordinate(5, 6)
        e = ResourceExhausted(coordinate=coord)
        assert e.coordinate == coord

    def test_is_frozen(self) -> None:
        e = ResourceExhausted(coordinate=Coordinate(0, 0))
        with pytest.raises((AttributeError, TypeError)):
            e.coordinate = Coordinate(1, 1)  # type: ignore[misc]
