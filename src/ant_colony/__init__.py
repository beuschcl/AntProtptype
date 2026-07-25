"""ant_colony – observable ant-colony simulation (world foundation).

Public sub-packages
-------------------
``ant_colony.domain``
    Pure domain model: coordinates, terrain, world objects, the World
    aggregate, events, and read-only snapshots.

``ant_colony.simulation``
    Fixed-tick deterministic engine powered by seeded randomness.

``ant_colony.scenario``
    TOML-based scenario loader that constructs domain objects.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("ant-colony")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
