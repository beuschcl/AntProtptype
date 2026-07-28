import pytest

from ant_colony.components import ResourceType
from ant_colony.entities.resource import Resource


def create_resource(
    *,
    value: int = 5,
    quantity: int = 3,
) -> Resource:
    return Resource(
        resource_id=1,
        x=100,
        y=200,
        resource_type=ResourceType.FOOD,
        value=value,
        quantity=quantity,
        radius=10,
        color=(1, 2, 3),
        discoverable_radius=30,
    )


def test_resource_exposes_properties() -> None:
    resource = create_resource()

    assert resource.resource_type is ResourceType.FOOD
    assert resource.value == 5
    assert resource.quantity == 3
    assert not resource.is_depleted


def test_resource_collects_portion() -> None:
    resource = create_resource()

    portion = resource.collect()

    assert portion is not None
    assert portion.source_id == resource.id
    assert portion.resource_type is ResourceType.FOOD
    assert portion.value == 5
    assert resource.quantity == 2


def test_resource_becomes_depleted() -> None:
    resource = create_resource(quantity=1)

    resource.collect()

    assert resource.is_depleted
    assert resource.collect() is None
    assert resource.shapes() == ()


@pytest.mark.parametrize(
    ("value", "quantity"),
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_resource_rejects_invalid_values(
    value: int,
    quantity: int,
) -> None:
    with pytest.raises(ValueError):
        create_resource(
            value=value,
            quantity=quantity,
        )