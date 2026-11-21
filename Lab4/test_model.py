"""Тести моделі, множинного успадкування та повторного використання Show."""
import gc
import unittest
import weakref
from unittest.mock import patch
from editor import MyEditor, CAPACITY
from shapes import (Shape, PointShape, LineShape, RectShape, EllipseShape,
                    LineWithCirclesShape, CubeShape)
from tools import TOOLS


class CanvasStub:
    def __init__(self):
        self.calls = []

    def create_line(self, *coords, **style):
        self.calls.append(('line', coords, style))

    def create_rectangle(self, *coords, **style):
        self.calls.append(('rectangle', coords, style))

    def create_oval(self, *coords, **style):
        self.calls.append(('oval', coords, style))


class ModelTests(unittest.TestCase):
    def test_abstract_and_multiple_inheritance(self):
        with self.assertRaises(TypeError):
            Shape(0, 0, 1, 1)
        self.assertTrue(issubclass(LineWithCirclesShape, LineShape))
        self.assertTrue(issubclass(LineWithCirclesShape, EllipseShape))
        self.assertTrue(issubclass(CubeShape, RectShape))
        self.assertTrue(issubclass(CubeShape, LineShape))
        self.assertEqual(CubeShape.__mro__.count(Shape), 1)
        self.assertEqual(LineWithCirclesShape.__mro__.count(Shape), 1)

    def test_original_geometry_and_styles(self):
        for x in (20, 80):
            for y in (30, 90):
                self.assertEqual(RectShape(50, 60, x, y).bounds(),
                                 (20, 30, 80, 90))
        c = CanvasStub()
        RectShape(50, 60, 80, 90).Show(c)
        EllipseShape(80, 90, 20, 30).Show(c)
        self.assertEqual(c.calls[0][2]['fill'], '#808080')
        self.assertEqual(c.calls[1][1], (20, 30, 80, 90))
        self.assertEqual(c.calls[1][2]['fill'], '')
        for _, _, style in c.calls:
            self.assertEqual(style['outline'], 'black')
            self.assertEqual(style['dash'], ())

    def test_all_previews_are_red_dashed_unfilled(self):
        for tool in TOOLS:
            with self.subTest(tool=tool.key):
                c = CanvasStub()
                tool.shape(30, 40, 120, 150).Show(c, preview=True)
                self.assertTrue(c.calls)
                for kind, _, style in c.calls:
                    self.assertEqual(style['dash'], (4, 3))
                    self.assertEqual(style.get('outline', style['fill']), 'red')
                    if kind != 'line':
                        self.assertEqual(style['fill'], '')

    def test_circles_reuse_base_show_without_mutation(self):
        c = CanvasStub()
        s = LineWithCirclesShape(20, 30, 80, 70)
        with patch.object(LineShape, 'Show', autospec=True) as line:
            with patch.object(EllipseShape, 'Show', autospec=True) as oval:
                s.Show(c)
                self.assertEqual(line.call_count, 1)
                self.assertEqual(oval.call_count, 2)
        s.Show(c)
        self.assertEqual([x[0] for x in c.calls], ['line','oval','oval'])
        self.assertEqual(c.calls[1][1], (13, 23, 27, 37))
        self.assertEqual(c.calls[2][1], (73, 63, 87, 77))
        self.assertEqual(s._coords, (20, 30, 80, 70))

    def test_cube_square_faces_and_twelve_edges(self):
        for coords in ((10,20,110,150), (110,150,10,20)):
            s = CubeShape(*coords)
            front, back = s.faces()
            self.assertEqual(front, (10,20,110,120))
            self.assertEqual(back, (40,-10,140,90))
            c = CanvasStub()
            s.Show(c)
            self.assertEqual([v[0] for v in c.calls],
                             ['rectangle'] * 2 + ['line'] * 4)
            for kind, _, style in c.calls:
                if kind == 'rectangle':
                    self.assertEqual(style['fill'], '')
            with patch.object(RectShape, 'Show', autospec=True) as rect:
                with patch.object(LineShape, 'Show', autospec=True) as line:
                    s.Show(c)
                    self.assertEqual(rect.call_count, 2)
                    self.assertEqual(line.call_count, 4)

    def test_zero_size_shapes_do_not_fail(self):
        for tool in TOOLS:
            tool.shape(1, 1, 1, 1).Show(CanvasStub(), True)

    def test_capacity_clear_and_close(self):
        e = MyEditor()
        for _ in range(CAPACITY):
            self.assertTrue(e.begin(10, 10))
            self.assertTrue(e.finish(20, 20))
        self.assertFalse(e.begin(0, 0))
        self.assertFalse(e.finish(0, 0))
        self.assertEqual(e.count, 117)
        shape_ref = weakref.ref(e._shapes[0])
        e.clear()
        self.assertEqual(e.count, 0)
        self.assertIsNone(shape_ref())
        self.assertTrue(e.begin(1, 1))
        e.close()
        e.close()
        self.assertTrue(e.closed)
        self.assertFalse(e.finish(2, 2))
        self.assertFalse(e.begin(3, 3))
        reference = weakref.ref(e)
        del e
        gc.collect()
        self.assertIsNone(reference())

    def test_selection_cancel_and_polymorphic_drawing(self):
        e = MyEditor()
        e.begin(0, 0)
        e.update(20, 30)
        e.select('cube')
        self.assertFalse(e.finish(20, 30))
        self.assertEqual(e.count, 0)
        with self.assertRaises(ValueError):
            e.select('missing')
        for tool in TOOLS:
            e.select(tool.key)
            e.begin(30, 40)
            e.finish(100, 100)
        c = CanvasStub()
        e.Show(c)
        self.assertEqual(e.count, 6)
        self.assertEqual(len(c.calls), 13)
        self.assertEqual(len({t.key for t in TOOLS}), len(TOOLS))


if __name__ == '__main__':
    unittest.main()
