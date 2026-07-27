from ant_colony.components import (
    ResourcePortion,
    ResourceType,
)
from ant_colony.entities.entity import Entity
from ant_colony.graphics.primitives import Circle, Shape

Color = tuple[int, int, int]


class Resource(Entity):
    def __init__(
        self,
        resource_id: int,
        x: float,
        y: float,
        resource_type: ResourceType,
        value: int,
        quantity: int,
        radius: float,
        color: Color,
        discoverable_radius: float,
    ) -> None:
        if value <= 0:
            raise ValueError(
                "Resource value must be greater than zero."
            )

        if quantity <= 0:
            raise ValueError(
                "Resource quantity must be greater than zero."
            )

        if radius <= 0:
            raise ValueError(
                "Resource radius must be greater than zero."
            )

        super().__init__(
            entity_id=resource_id,
            x=x,
            y=y,
            discoverable_radius=discoverable_radius,
        )

        self._resource_type = resource_type
        self._value = value
        self._quantity = quantity
        self._radius = radius
        self._color = color

    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type

    @property
    def value(self) -> int:
        return self._value

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def is_depleted(self) -> bool:
        return self._quantity == 0

    def collect(self) -> ResourcePortion | None:
        if self.is_depleted:
            return None

        self._quantity -= 1

        return ResourcePortion(
            source_id=self.id,
            resource_type=self.resource_type,
            value=self.value,
        )

    def shapes(self) -> tuple[Shape, ...]:
        if self.is_depleted:
            return ()

        return (
            Circle(
                x=self.x,
                y=self.y,
                radius=self._radius,
                color=self._color,
            ),
        )