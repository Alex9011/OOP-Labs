import tempfile
import unittest
from pathlib import Path

from editor import CAPACITY
from shape_csv import load_shapes, save_shapes
from tools import TOOLS


class CsvTests(unittest.TestCase):
    def test_round_trip_all_shapes_and_empty_scene(self):
        shapes = [tool.shape(10, -5, 42, 30) for tool in TOOLS]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'фігури.csv'
            save_shapes(path, shapes)
            restored = load_shapes(path)
            self.assertEqual([(type(s), s.coords) for s in restored],
                             [(type(s), s.coords) for s in shapes])
            save_shapes(path, ())
            self.assertEqual(load_shapes(path), [])

    def test_rejects_invalid_rows_and_overflow(self):
        header = 'type,x1,y1,x2,y2\n'
        bad_contents = ('name,x1,y1,x2,y2\n',
                        header + 'triangle,1,2,3,4\n',
                        header + 'point,1,2,3\n',
                        header + 'point,a,2,3,4\n',
                        header + 'point,1,2,1000001,4\n',
                        header + 'point,1,2,3,4\n' * (CAPACITY + 1))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            for contents in bad_contents:
                with self.subTest(first_lines=contents[:60]):
                    path.write_text(contents)
                    with self.assertRaises(ValueError):
                        load_shapes(path)
