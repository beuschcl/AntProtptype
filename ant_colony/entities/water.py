from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.resource import Resource


class Water(Resource):
    def __init__(
        self,
        water_id: int,
        x: float,
        y: float,
        hydration: int,
        quantity: int = 1,
    ) -> None:
        super().__init__(
            resource_id=water_id,
            x=x,
            y=y,
            resource_type=ResourceType.WATER,
            value=hydration,
            quantity=quantity,
            radius=settings.WATER_RADIUS,
            color=settings.WATER_COLOR,
            discoverable_radius=(
                settings.WATER_DISCOVERABLE_RADIUS
            ),
        )

    @property
    def hydration(self) -> int:
        return self.value