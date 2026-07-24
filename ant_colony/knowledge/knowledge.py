#ant_colony/knowledge/knowledge.py
from ant_colony.knowledge.memory import Memory


class Knowledge:

    def __init__(self):

        self.memories = []

    def remember(self, name, value):

        self.memories.append(
            Memory(name, value)
        )

    def __repr__(self):

        return str(self.memories)

    def count(self):
        return len(self.memories)