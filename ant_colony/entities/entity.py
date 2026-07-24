#entities/entity.py
class Entity:

    def __init__(
        self,
        entity_id,
        x,
        y,
        discoverable_radius,
    ):

        self.id = entity_id
        self.x = x
        self.y = y
        self.discoverable_radius = discoverable_radius

    def distance_to(self, other):

        dx = self.x - other.x
        dy = self.y - other.y

        return (dx * dx + dy * dy) ** 0.5

    def shapes(self):

        return []