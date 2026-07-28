from ant_colony.knowledge import Knowledge, Memory


def test_knowledge_starts_empty() -> None:
    knowledge = Knowledge()

    assert knowledge.count() == 0
    assert knowledge.memories == ()


def test_remember_stores_memory() -> None:
    knowledge = Knowledge()

    memory = knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert memory == Memory(
        name="food_location",
        value=(200, 200),
    )
    assert knowledge.count() == 1


def test_recall_returns_remembered_value() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    result = knowledge.recall("food_location")

    assert result == (200, 200)


def test_recall_returns_none_for_unknown_memory() -> None:
    knowledge = Knowledge()

    assert knowledge.recall("unknown") is None


def test_remember_updates_existing_memory() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    knowledge.remember(
        "food_location",
        (300, 250),
    )

    assert knowledge.recall("food_location") == (300, 250)
    assert knowledge.count() == 1


def test_knows_reports_known_memory() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert knowledge.knows("food_location")
    assert not knowledge.knows("nest_location")


def test_forget_removes_memory() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    removed = knowledge.forget("food_location")

    assert removed
    assert not knowledge.knows("food_location")
    assert knowledge.count() == 0


def test_forget_returns_false_for_unknown_memory() -> None:
    knowledge = Knowledge()

    assert not knowledge.forget("unknown")


def test_share_with_copies_memories() -> None:
    source = Knowledge()
    destination = Knowledge()

    source.remember(
        "food_location",
        (200, 200),
    )
    source.remember(
        "nest_location",
        (500, 350),
    )

    shared_count = source.share_with(destination)

    assert shared_count == 2
    assert destination.recall("food_location") == (200, 200)
    assert destination.recall("nest_location") == (500, 350)


def test_share_with_updates_different_value() -> None:
    source = Knowledge()
    destination = Knowledge()

    source.remember(
        "food_location",
        (300, 250),
    )
    destination.remember(
        "food_location",
        (200, 200),
    )

    shared_count = source.share_with(destination)

    assert shared_count == 1
    assert destination.recall("food_location") == (300, 250)


def test_share_with_does_not_count_identical_memory() -> None:
    source = Knowledge()
    destination = Knowledge()

    source.remember(
        "food_location",
        (200, 200),
    )
    destination.remember(
        "food_location",
        (200, 200),
    )

    shared_count = source.share_with(destination)

    assert shared_count == 0
    assert destination.count() == 1


def test_memories_property_is_read_only_tuple() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert isinstance(knowledge.memories, tuple)


def test_knowledge_can_be_iterated() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )
    knowledge.remember(
        "nest_location",
        (500, 350),
    )

    memory_names = {memory.name for memory in knowledge}

    assert memory_names == {
        "food_location",
        "nest_location",
    }


def test_len_returns_memory_count() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert len(knowledge) == 1


def test_contains_checks_memory_name() -> None:
    knowledge = Knowledge()
    knowledge.remember(
        "food_location",
        (200, 200),
    )

    assert "food_location" in knowledge
    assert "nest_location" not in knowledge
