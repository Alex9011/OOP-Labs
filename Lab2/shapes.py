"""Фігури: спільний інтерфейс і поліморфне малювання на Canvas."""
from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self, x1, y1, x2, y2):
        self._coords = (x1, y1, x2, y2)

    @abstractmethod
    def show(self, canvas, preview=False):
        """Намалювати об'єкт; preview — лише чорний контур."""

    def bounds(self):
        x1, y1, x2, y2 = self._coords
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


class PointShape(Shape):
    def show(self, canvas, preview=False):
        x, y, _, _ = self._coords
        canvas.create_oval(x-2, y-2, x+2, y+2, fill='black', outline='black')


class LineShape(Shape):
    def show(self, canvas, preview=False):
        canvas.create_line(*self._coords, fill='black', width=1)


class RectShape(Shape):
    def show(self, canvas, preview=False):
        canvas.create_rectangle(*self.bounds(), outline='black', width=1,
                                fill='' if preview else '#FFA500')


class EllipseShape(Shape):
    def bounds(self):
        
        cx, cy, x, y = self._coords
        dx, dy = abs(x-cx), abs(y-cy)
        return cx-dx, cy-dy, cx+dx, cy+dy

    def show(self, canvas, preview=False):
        canvas.create_oval(*self.bounds(), outline='black', width=1,
                           fill='' if preview else 'white')
