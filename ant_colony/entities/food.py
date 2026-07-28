from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.resource import Resource
from ant_colony.graphics.primitives import Polygon, Shape


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
            discoverable_radius=(settings.FOOD_DISCOVERABLE_RADIUS),
        )

    @property
    def nutrition(self) -> int:
        return self.value

    def shapes(self) -> tuple[Shape, ...]:
        if self.is_depleted:
            return ()

        radius = settings.FOOD_RADIUS

        return (
            Polygon(
                points=(
                    (self.x, self.y - radius),
                    (self.x + radius, self.y),
                    (self.x, self.y + radius),
                    (self.x - radius, self.y),
                ),
                color=settings.FOOD_COLOR,
            ),
            Polygon(
                points=(
                    (self.x, self.y - radius),
                    (self.x + radius, self.y),
                    (self.x, self.y + radius),
                    (self.x - radius, self.y),
                ),
                color=settings.FOOD_OUTLINE_COLOR,
                width=2,
            ),
        )
