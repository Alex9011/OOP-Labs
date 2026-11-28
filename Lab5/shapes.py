"""Шість фігур; нові класи повторно використовують Show базових класів."""
from abc import ABC, abstractmethod


class Shape(ABC):
    COLOR = 'black'

    def __init__(self, x1, y1, x2, y2):
        self._coords = (x1, y1, x2, y2)

    @property
    def coords(self):
        """Початкові координати введення фігури."""
        return self._coords

    @abstractmethod
    def Show(self, canvas, preview=False):
        """Відобразити фігуру або її пунктирний гумовий слід."""

    def bounds(self):
        x1, y1, x2, y2 = self._coords
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def pen(self, preview):
        return {'width': 1, 'dash': (4, 3) if preview else ()}

    def color(self, preview):
        return 'red' if preview else self.COLOR


class PointShape(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x1, y1)

    def Show(self, canvas, preview=False):
        x, y, _, _ = self._coords
        r = 5 if preview else 2
        canvas.create_oval(x-r, y-r, x+r, y+r,
                           outline=self.color(preview),
                           fill='' if preview else self.COLOR,
                           **self.pen(preview))


class LineShape(Shape):
    def Show(self, canvas, preview=False, *, coords=None):
        canvas.create_line(*(self._coords if coords is None else coords),
                           fill=self.color(preview), **self.pen(preview))


class RectShape(Shape):
    def bounds(self):
        # Як у Lab3: початкова точка — центр прямокутника.
        cx, cy, x, y = self._coords
        dx, dy = abs(x-cx), abs(y-cy)
        return cx-dx, cy-dy, cx+dx, cy+dy

    def Show(self, canvas, preview=False, *, bounds=None, fill='#808080'):
        area = RectShape.bounds(self) if bounds is None else bounds
        canvas.create_rectangle(*area, outline=self.color(preview),
                                fill='' if preview else fill,
                                **self.pen(preview))


class EllipseShape(Shape):
    def Show(self, canvas, preview=False, *, bounds=None, fill=''):
        area = Shape.bounds(self) if bounds is None else bounds
        canvas.create_oval(*area, outline=self.color(preview),
                           fill='' if preview else fill,
                           **self.pen(preview))


class LineWithCirclesShape(LineShape, EllipseShape):
    """Множинне успадкування: лінія та два кружечки на її кінцях."""
    COLOR = '#174b8a'
    RADIUS = 7

    def Show(self, canvas, preview=False):
        LineShape.Show(self, canvas, preview)
        x1, y1, x2, y2 = self._coords
        r = self.RADIUS
        for x, y in ((x1, y1), (x2, y2)):
            EllipseShape.Show(self, canvas, preview,
                              bounds=(x-r, y-r, x+r, y+r), fill='white')


class CubeShape(RectShape, LineShape):
    """Дві квадратні грані та чотири ребра — каркас у проєкції."""
    COLOR = '#174b8a'

    def faces(self):
        x1, y1, x2, y2 = Shape.bounds(self)
        side = min(x2-x1, y2-y1)
        offset = side * 0.3
        front = (x1, y1, x1+side, y1+side)
        back = tuple(v + (offset if i % 2 == 0 else -offset)
                     for i, v in enumerate(front))
        return front, back

    def Show(self, canvas, preview=False):
        front, back = self.faces()
        # Порожнє заповнення дає каркас, а не дві непрозорі грані.
        RectShape.Show(self, canvas, preview, bounds=back, fill='')
        RectShape.Show(self, canvas, preview, bounds=front, fill='')
        x1, y1, x2, y2 = front
        bx1, by1, bx2, by2 = back
        corners = zip(((x1, y1), (x2, y1), (x2, y2), (x1, y2)),
                      ((bx1, by1), (bx2, by1), (bx2, by2), (bx1, by2)))
        for a, b in corners:
            LineShape.Show(self, canvas, preview, coords=(*a, *b))
