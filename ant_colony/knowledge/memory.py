from dataclasses import dataclass

type MemoryValue = object


@dataclass(frozen=True, slots=True)
class Memory:
    name: str
    value: MemoryValue

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Memory name cannot be empty.")

    def __repr__(self) -> str:
        return f"{self.name}: {self.value!r}"
