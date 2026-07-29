from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RectangleObstacle:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains_point(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.left <= x <= self.right
            and self.top <= y <= self.bottom
        )

    def intersects_circle(
        self,
        x: float,
        y: float,
        radius: float = 0.0,
    ) -> bool:
        nearest_x = min(max(x, self.left), self.right)
        nearest_y = min(max(y, self.top), self.bottom)
        dx = x - nearest_x
        dy = y - nearest_y
        return dx * dx + dy * dy <= radius * radius

    def intersects_segment(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        padding: float = 0.0,
    ) -> bool:
        x_min = self.left - padding
        x_max = self.right + padding
        y_min = self.top - padding
        y_max = self.bottom + padding

        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0

        if (
            x_min <= x0 <= x_max
            and y_min <= y0 <= y_max
        ):
            return True
        if (
            x_min <= x1 <= x_max
            and y_min <= y1 <= y_max
        ):
            return True

        t0 = 0.0
        t1 = 1.0

        for p, q in (
            (-dx, x0 - x_min),
            (dx, x_max - x0),
            (-dy, y0 - y_min),
            (dy, y_max - y0),
        ):
            if p == 0:
                if q < 0:
                    return False
                continue

            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False

        return True
