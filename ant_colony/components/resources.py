from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    FOOD = "food"
    WATER = "water"
    BUILDING_MATERIAL = "building_material"


@dataclass(frozen=True, slots=True)
class ResourcePortion:
    source_id: int | str
    resource_type: ResourceType
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(
                "Resource value must be greater than zero."
            )