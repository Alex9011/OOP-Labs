"""MyEditor керує моделлю й введенням незалежно від Tkinter."""
from tools import TOOL_BY_KEY

CAPACITY = 117  # Зберігаємо місткість попередньої Lab3.


class MyEditor:
    _instance = None
    _creation_key = object()

    @classmethod
    def instance(cls):
        """Створити редактор за першого звернення і надалі повертати його."""
        if cls._instance is None:
            cls._instance = cls(cls._creation_key)
        return cls._instance

    def __init__(self, key=None):
        if key is not self._creation_key:
            raise TypeError('Отримайте редактор через MyEditor.instance()')
        self._shapes = [None] * CAPACITY
        self._count = 0
        self._tool = 'point'
        self._start = None
        self._preview = None
        self._closed = False

    @property
    def count(self):
        return self._count

    @property
    def shapes(self):
        return tuple(self._shapes[:self._count])

    @property
    def tool(self):
        return self._tool

    @property
    def closed(self):
        return self._closed

    def select(self, key):
        if key not in TOOL_BY_KEY:
            raise ValueError(f'Невідомий інструмент: {key}')
        self.cancel()
        self._tool = key

    def begin(self, x, y):
        self.cancel()
        if self._closed or self._count >= CAPACITY:
            return False
        self._start = (x, y)
        self.update(x, y)
        return True

    def update(self, x, y):
        if self._start is not None:
            factory = TOOL_BY_KEY[self._tool].shape
            self._preview = factory(*self._start, x, y)

    def finish(self, x, y):
        if self._start is None:
            return False
        self.update(x, y)
        self._shapes[self._count] = self._preview
        self._count += 1
        self.cancel()
        return True

    def cancel(self):
        self._start = None
        self._preview = None

    def clear(self):
        self.cancel()
        for i in range(self._count):
            self._shapes[i] = None
        self._count = 0

    def remove(self, index):
        if not 0 <= index < self._count:
            return False
        self.cancel()
        for i in range(index, self._count - 1):
            self._shapes[i] = self._shapes[i + 1]
        self._count -= 1
        self._shapes[self._count] = None
        return True

    def replace(self, shapes):
        if self._closed:
            raise ValueError('Редактор закрито.')
        if len(shapes) > CAPACITY:
            raise ValueError(f'Можна завантажити до {CAPACITY} фігур.')
        self.clear()
        self._count = len(shapes)
        self._shapes[:self._count] = shapes

    def Show(self, canvas, selected=None):
        selection_bounds = None
        for i in range(self._count):
            if i == selected:
                first = len(canvas.find_all())
            self._shapes[i].Show(canvas)
            if i == selected:
                items = canvas.find_all()[first:]
                if items:
                    selection_bounds = canvas.bbox(*items)
        if self._preview is not None:
            self._preview.Show(canvas, preview=True)
        if selection_bounds is not None:
            x1, y1, x2, y2 = selection_bounds
            canvas.create_rectangle(x1-5, y1-5, x2+5, y2+5,
                                    outline='#087e73', width=2, dash=(5, 3),
                                    tags=('selection',))

    def close(self):
        # Явно прибираємо посилання; повторний виклик безпечний.
        self.clear()
        self._closed = True
        if type(self)._instance is self:
            type(self)._instance = None
