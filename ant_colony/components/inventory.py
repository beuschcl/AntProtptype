#ant_colony/components/inventory.py
class Inventory:

    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        self.items.remove(item)

    def count(self):
        return len(self.items)