"""Єдиний реєстр: фабрики фігур, підписи меню та іконки панелі."""
from dataclasses import dataclass
from shapes import (Shape, PointShape, LineShape, RectShape, EllipseShape,
                    LineWithCirclesShape, CubeShape)


@dataclass(frozen=True)
class Tool:
    key: str
    label: str
    icon: str
    shape: type[Shape]


TOOLS = (
    Tool('point', 'Крапка', 'point.png', PointShape),
    Tool('line', 'Лінія', 'line.png', LineShape),
    Tool('rectangle', 'Прямокутник', 'rectangle.png', RectShape),
    Tool('ellipse', 'Еліпс', 'ellipse.png', EllipseShape),
    Tool('circles', 'Лінія з кружечками', 'circles.png', LineWithCirclesShape),
    Tool('cube', 'Каркас куба', 'cube.png', CubeShape),
)
TOOL_BY_KEY = {tool.key: tool for tool in TOOLS}
