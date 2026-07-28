from collections.abc import Iterator

from ant_colony.knowledge.memory import Memory, MemoryValue


class Knowledge:
    def __init__(self) -> None:
        self._memories: dict[str, Memory] = {}

    @property
    def memories(self) -> tuple[Memory, ...]:
        return tuple(self._memories.values())

    def remember(
        self,
        name: str,
        value: MemoryValue,
    ) -> Memory:
        memory = Memory(
            name=name,
            value=value,
        )

        self._memories[memory.name] = memory

        return memory

    def recall(self, name: str) -> MemoryValue | None:
        memory = self._memories.get(name)

        if memory is None:
            return None

        return memory.value

    def knows(self, name: str) -> bool:
        return name in self._memories

    def forget(self, name: str) -> bool:
        if name not in self._memories:
            return False

        del self._memories[name]
        return True

    def share_with(self, other: "Knowledge") -> int:
        shared_count = 0

        for memory in self._memories.values():
            existing_value = other.recall(memory.name)

            if (
                not other.knows(memory.name)
                or existing_value != memory.value
            ):
                other.remember(
                    memory.name,
                    memory.value,
                )
                shared_count += 1

        return shared_count

    def count(self) -> int:
        return len(self._memories)

    def __iter__(self) -> Iterator[Memory]:
        return iter(self._memories.values())

    def __contains__(self, name: object) -> bool:
        return name in self._memories

    def __len__(self) -> int:
        return self.count()

    def __repr__(self) -> str:
        return f"Knowledge(memories={self.memories!r})"