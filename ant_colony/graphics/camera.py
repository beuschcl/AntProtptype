#ant_colony/graphics/camera.py
class Camera:

    def __init__(self):

        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

    def world_to_screen(self, x, y):

        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom

        return (
            int(screen_x),
            int(screen_y),
        )

    def screen_to_world(self, x, y):

        world_x = x / self.zoom + self.x
        world_y = y / self.zoom + self.y

        return (
            world_x,
            world_y,
        )