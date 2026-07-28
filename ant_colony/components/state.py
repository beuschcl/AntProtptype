from enum import Enum


class AntState(Enum):
    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    CARRYING_FOOD = "carrying_food"
    SEEKING_WATER = "seeking_water"


class FoodTargetSource(Enum):
    DISCOVERY = "discovery"
    PHEROMONE = "pheromone"
    MEMORY = "memory"
