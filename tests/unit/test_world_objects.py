"""Unit tests for world objects (Obstacle, Resource, Nest)."""

from __future__ import annotations

import pytest

from ant_colony.domain.world_objects import Nest, Obstacle, Resource


class TestObstacle:
    def test_blocks_traversal(self) -> None:
        assert Obstacle().blocks_traversal is True

    def test_kind(self) -> None:
        assert Obstacle().kind == "obstacle"

    def test_repr(self) -> None:
        assert repr(Obstacle()) == "Obstacle()"


class TestResource:
    def test_stores_amount_and_max(self) -> None:
        r = Resource(50, 100)
        assert r.amount == 50
        assert r.max_amount == 100

    def test_defaults_max_to_amount(self) -> None:
        r = Resource(30)
        assert r.max_amount == 30

    def test_not_exhausted_initially(self) -> None:
        assert not Resource(10).is_exhausted

    def test_does_not_block_traversal(self) -> None:
        assert Resource(10).blocks_traversal is False

    def test_kind(self) -> None:
        assert Resource(10).kind == "resource"

    def test_deplete_partial(self) -> None:
        r = Resource(100)
        removed = r._deplete(30)
        assert removed == 30
        assert r.amount == 70
        assert not r.is_exhausted

    def test_deplete_exact(self) -> None:
        r = Resource(50)
        removed = r._deplete(50)
        assert removed == 50
        assert r.is_exhausted

    def test_deplete_more_than_available_caps_at_zero(self) -> None:
        r = Resource(10)
        removed = r._deplete(999)
        assert removed == 10
        assert r.amount == 0
        assert r.is_exhausted

    def test_deplete_zero_raises(self) -> None:
        r = Resource(10)
        with pytest.raises(ValueError, match="positive"):
            r._deplete(0)

    def test_deplete_negative_raises(self) -> None:
        r = Resource(10)
        with pytest.raises(ValueError):
            r._deplete(-5)

    def test_invalid_amount_raises(self) -> None:
        with pytest.raises(ValueError):
            Resource(0)

    def test_amount_exceeds_max_raises(self) -> None:
        with pytest.raises(ValueError):
            Resource(200, 100)

    def test_negative_max_raises(self) -> None:
        with pytest.raises(ValueError):
            Resource(10, -1)

    def test_repr(self) -> None:
        r = Resource(5, 10)
        assert "5" in repr(r)
        assert "10" in repr(r)


class TestNest:
    def test_does_not_block_traversal(self) -> None:
        assert Nest().blocks_traversal is False

    def test_kind(self) -> None:
        assert Nest().kind == "nest"

    def test_repr(self) -> None:
        assert repr(Nest()) == "Nest()"
