from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.resource import Resource


class Food(Resource):
    def __init__(
        self,
        food_id: int,
        x: float,
        y: float,
        nutrition: int,
        quantity: int = 1,
    ) -> None:
        super().__init__(
            resource_id=food_id,
            x=x,
            y=y,
            resource_type=ResourceType.FOOD,
            value=nutrition,
            quantity=quantity,
            radius=settings.FOOD_RADIUS,
            color=settings.FOOD_COLOR,
            discoverable_radius=(
                settings.FOOD_DISCOVERABLE_RADIUS
            ),
        )

    @property
    def nutrition(self) -> int:
        return self.value