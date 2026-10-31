"""Модель редактора: фіксовані 116 місць для посилань на об'єкти."""
from shapes import PointShape, LineShape, RectShape, EllipseShape

N = 116
SHAPE_TYPES = {'Крапка': PointShape, 'Лінія': LineShape,
               'Прямокутник': RectShape, 'Еліпс': EllipseShape}


class Editor:
    def __init__(self):
        self._shapes = [None] * N
        self._count = 0

    @property
    def count(self):
        return self._count

    def add(self, shape):
        if self._count == N:
            return False
        self._shapes[self._count] = shape
        self._count += 1
        return True

    def clear(self):
        for i in range(self._count):
            self._shapes[i] = None
        self._count = 0

    def show(self, canvas):
        for i in range(self._count):
            self._shapes[i].show(canvas)
