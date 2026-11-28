"""Запис і читання завершених фігур у форматі CSV."""
import csv
from pathlib import Path
from tempfile import NamedTemporaryFile

from editor import CAPACITY
from tools import TOOL_BY_CLASS, TOOL_BY_KEY

HEADER = ('type', 'x1', 'y1', 'x2', 'y2')
COORD_LIMIT = 1_000_000


def save_shapes(path, shapes):
    path = Path(path)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.writer(stream)
            writer.writerow(HEADER)
            for shape in shapes:
                writer.writerow((TOOL_BY_CLASS[type(shape)].key, *shape.coords))
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_shapes(path):
    shapes = []
    with open(path, encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != list(HEADER):
            raise ValueError('Потрібен заголовок type,x1,y1,x2,y2.')
        for row in reader:
            line = reader.line_num
            if len(shapes) == CAPACITY:
                raise ValueError(f'Файл містить понад {CAPACITY} фігур.')
            if len(row) != len(HEADER):
                raise ValueError(f'Рядок {line}. Потрібно п’ять полів.')
            tool = TOOL_BY_KEY.get(row[0])
            if tool is None:
                raise ValueError(f'Рядок {line}. Невідомий тип фігури.')
            try:
                coords = tuple(int(value) for value in row[1:])
            except ValueError as error:
                raise ValueError(f'Рядок {line}. Координати мають бути цілими.') from error
            if any(abs(value) > COORD_LIMIT for value in coords):
                raise ValueError(f'Рядок {line}. Допустимі координати ±{COORD_LIMIT}.')
            shapes.append(tool.shape(*coords))
    return shapes
