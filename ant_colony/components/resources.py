from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    FOOD = "food"


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