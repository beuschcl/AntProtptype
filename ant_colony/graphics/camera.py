class Camera:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

    def world_to_screen(
        self,
        x: float,
        y: float,
    ) -> tuple[int, int]:
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom

        return (
            round(screen_x),
            round(screen_y),
        )

    def screen_to_world(
        self,
        x: float,
        y: float,
    ) -> tuple[float, float]:
        world_x = x / self.zoom + self.x
        world_y = y / self.zoom + self.y

        return (
            world_x,
            world_y,
        )

    def scale_length(self, length: float) -> int:
        return max(1, round(length * self.zoom))