"""MyEditor керує моделлю й введенням незалежно від Tkinter."""
from tools import TOOL_BY_KEY

CAPACITY = 117  # Зберігаємо місткість попередньої Lab3.


class MyEditor:
    def __init__(self):
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

    def Show(self, canvas):
        for i in range(self._count):
            self._shapes[i].Show(canvas)
        if self._preview is not None:
            self._preview.Show(canvas, preview=True)

    def close(self):
        # Явно прибираємо посилання; повторний виклик безпечний.
        self.clear()
        self._closed = True
