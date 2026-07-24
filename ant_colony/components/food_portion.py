from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoodPortion:
    source_food_id: int
    nutrition: int

    def __post_init__(self) -> None:
        if self.nutrition <= 0:
            raise ValueError(
                "Food portion nutrition must be positive."
            )