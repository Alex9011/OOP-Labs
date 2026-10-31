"""Перевірки логіки без графічного дисплея: python -m unittest -v."""
import unittest
from editor import Editor, N
from shapes import Shape, RectShape, EllipseShape, PointShape, LineShape

class CanvasStub:
    def __init__(self): self.calls = []
    def create_rectangle(self, *args, **kwargs): self.calls.append(('rect', args, kwargs))
    def create_oval(self, *args, **kwargs): self.calls.append(('oval', args, kwargs))
    def create_line(self, *args, **kwargs): self.calls.append(('line', args, kwargs))

class ModelTests(unittest.TestCase):
    def test_capacity_and_clear(self):
        editor = Editor()
        for _ in range(N): self.assertTrue(editor.add(PointShape(1, 2, 1, 2)))
        self.assertFalse(editor.add(PointShape(3, 4, 3, 4)))
        self.assertEqual(editor.count, 116)
        editor.clear()
        self.assertEqual(editor.count, 0)
        self.assertTrue(editor.add(LineShape(1, 2, 3, 4)))

    def test_geometry_all_directions(self):
        for x in (20, 80):
            for y in (30, 90):
                self.assertEqual(EllipseShape(50, 60, x, y).bounds(), (20, 30, 80, 90))
        self.assertEqual(RectShape(80, 90, 20, 30).bounds(), (20, 30, 80, 90))

    def test_fills_preview_and_polymorphism(self):
        canvas = CanvasStub()
        editor = Editor()
        for cls in (PointShape, LineShape, RectShape, EllipseShape):
            editor.add(cls(10, 10, 20, 20))
        editor.show(canvas)
        self.assertEqual(len(canvas.calls), 4)
        self.assertEqual(canvas.calls[2][2]['fill'], '#FFA500')
        self.assertEqual(canvas.calls[3][2]['fill'], 'white')
        for cls in (RectShape, EllipseShape):
            cls(10, 10, 20, 20).show(canvas, True)
            self.assertEqual(canvas.calls[-1][2]['fill'], '')
            self.assertEqual(canvas.calls[-1][2]['outline'], 'black')

    def test_abstract_shape(self):
        with self.assertRaises(TypeError): Shape(0, 0, 1, 1)

if __name__ == '__main__': unittest.main()
