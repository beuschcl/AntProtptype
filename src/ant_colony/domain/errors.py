"""Domain-specific error types for the ant-colony simulation."""

from __future__ import annotations


class AntColonyError(Exception):
    """Base class for all ant-colony domain errors."""


class InvalidCoordinateError(AntColonyError):
    """Raised when a coordinate is outside world bounds."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__(
            f"Coordinate ({x}, {y}) is outside world bounds [0, {width}) x [0, {height})"
        )
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class OccupancyConflictError(AntColonyError):
    """Raised when two incompatible objects are placed at the same coordinate."""

    def __init__(self, x: int, y: int, existing: str, incoming: str) -> None:
        super().__init__(f"Cannot place {incoming} at ({x}, {y}): already occupied by {existing}")
        self.x = x
        self.y = y
        self.existing = existing
        self.incoming = incoming


class NoResourceError(AntColonyError):
    """Raised when a resource operation targets a coordinate with no resource."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(f"No resource at ({x}, {y})")
        self.x = x
        self.y = y


class ResourceExhaustedError(AntColonyError):
    """Raised when attempting to deplete a resource that is already exhausted."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(f"Resource at ({x}, {y}) is already exhausted")
        self.x = x
        self.y = y


class InvalidScenarioError(AntColonyError):
    """Raised when a scenario configuration is invalid or inconsistent."""
