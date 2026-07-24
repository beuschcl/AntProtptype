#ant_colony/entities/nest.py
from ant_colony.components.inventory import Inventory


class Nest:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.inventory = Inventory()

    def store(self, item):

        self.inventory.add(item)