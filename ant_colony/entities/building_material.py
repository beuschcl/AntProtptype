from ant_colony.components import ResourceType
from ant_colony.config import settings
from ant_colony.entities.resource import Resource
from ant_colony.graphics.primitives import Polygon, Shape


class BuildingMaterial(Resource):
    def __init__(
        self,
        material_id: int,
        x: float,
        y: float,
        construction_value: int,
        quantity: int = 1,
    ) -> None:
        super().__init__(
            resource_id=material_id,
            x=x,
            y=y,
            resource_type=(ResourceType.BUILDING_MATERIAL),
            value=construction_value,
            quantity=quantity,
            radius=(settings.BUILDING_MATERIAL_RADIUS),
            color=(settings.BUILDING_MATERIAL_COLOR),
            discoverable_radius=(settings.BUILDING_MATERIAL_DISCOVERABLE_RADIUS),
        )

    @property
    def construction_value(self) -> int:
        return self.value

    def shapes(self) -> tuple[Shape, ...]:
        if self.is_depleted:
            return ()

        radius = settings.BUILDING_MATERIAL_RADIUS

        return (
            Polygon(
                points=(
                    (self.x - radius, self.y - radius),
                    (self.x + radius, self.y - radius),
                    (self.x + radius, self.y + radius),
                    (self.x - radius, self.y + radius),
                ),
                color=settings.BUILDING_MATERIAL_COLOR,
            ),
            Polygon(
                points=(
                    (self.x - radius, self.y - radius),
                    (self.x + radius, self.y - radius),
                    (self.x + radius, self.y + radius),
                    (self.x - radius, self.y + radius),
                ),
                color=settings.BUILDING_MATERIAL_OUTLINE_COLOR,
                width=2,
            ),
        )
