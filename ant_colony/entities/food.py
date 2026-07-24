#ant_colony/entities/food.py
from ant_colony.config import settings


class Food:

    def __init__(self, x, y, nutrition):

        self.x = x
        self.y = y

        self.nutrition = nutrition
        self.decay_timer = settings.FOOD_DECAY_TIME

    def consume(self):

        if self.nutrition > 0:
            self.nutrition -= 1
            return True

        return False

    def update(self):

        self.decay_timer -= 1