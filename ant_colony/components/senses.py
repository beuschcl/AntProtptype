#ant_colony/components/senses.py
from ant_colony.config import settings


class Senses:

    def __init__(self):

        self.radius = settings.ANT_SENSE_RADIUS