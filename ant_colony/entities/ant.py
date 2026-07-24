#ant_colony/entities/ant.py
from ant_colony.components.inventory import Inventory
from ant_colony.knowledge.knowledge import Knowledge


class Ant:

    def __init__(self, ant_id):

        self.id = ant_id

        self.inventory = Inventory()
        self.knowledge = Knowledge()

    def __repr__(self):

        return f"Ant(id={self.id})"