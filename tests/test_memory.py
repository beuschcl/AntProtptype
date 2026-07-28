import pytest

from ant_colony.knowledge import Memory


def test_memory_stores_name_and_value() -> None:
    memory = Memory(
        name="food_location",
        value=(200, 200),
    )

    assert memory.name == "food_location"
    assert memory.value == (200, 200)


def test_memory_is_immutable() -> None:
    memory = Memory(
        name="food_location",
        value=(200, 200),
    )

    with pytest.raises(AttributeError):
        memory.name = "nest_location"


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "\t",
    ],
)
def test_memory_rejects_empty_name(name: str) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        Memory(
            name=name,
            value=(200, 200),
        )