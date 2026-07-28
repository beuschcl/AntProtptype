from enum import Enum


class AntState(Enum):
    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    CARRYING_FOOD = "carrying_food"


class FoodTargetSource(Enum):
    DISCOVERY = "discovery"
    MEMORY = "memory"
