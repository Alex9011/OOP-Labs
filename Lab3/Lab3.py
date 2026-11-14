"""Lab3, варіант 17. Запуск: python Lab3.py (Python 3 + Tkinter)."""
import tkinter as tk
from tkinter import messagebox
from editor import Editor, SHAPE_TYPES, N
from toolbar import ShapeToolbar


class Application:
    def __init__(self, root):
        self.root = root
        self.editor = Editor()
        self.kind = tk.StringVar(value='Крапка')
        self.start = None
        self.preview = None
        root.title('Lab3 — Варіант 17 — Крапка')
        root.geometry('900x600')
        root.minsize(480, 320)
        bar = tk.Menu(root)
        file_menu = tk.Menu(bar, tearoff=False)
        file_menu.add_command(label='Очистити', command=self.clear)
        file_menu.add_separator()
        file_menu.add_command(label='Вихід', command=root.destroy)
        bar.add_cascade(label='Файл', menu=file_menu)
        self.objects_menu = tk.Menu(bar, tearoff=False, postcommand=self.OnInitMenuPopup)
        for name in SHAPE_TYPES:
            self.objects_menu.add_radiobutton(label=name, variable=self.kind,
                                             value=name, command=self.select_shape)
        bar.add_cascade(label='Об’єкти', menu=self.objects_menu)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label='Про програму', command=self.about)
        bar.add_cascade(label='Довідка', menu=help_menu)
        root.config(menu=bar)
        self.toolbar = ShapeToolbar(root, self.kind, self.select_shape)
        self.toolbar.pack(side="top", fill="x")
        self.status = tk.StringVar()
        tk.Label(root, textvariable=self.status, anchor='w').pack(side='bottom', fill='x')
        self.canvas = tk.Canvas(root, background='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<ButtonPress-1>', self.press)
        self.canvas.bind('<B1-Motion>', self.move)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<Configure>', self.configure)
        root.bind('<Escape>', self.cancel)
        root.bind('<FocusOut>', self.focus_out)
        self.redraw()

    def OnInitMenuPopup(self):
        self.toolbar.sync()

    def select_shape(self):
        self.cancel()
        self.toolbar.sync()
        self.root.title(f'Lab3 — Варіант 17 — {self.kind.get()}')

    def configure(self, event):
        self.redraw()

    def about(self):
        messagebox.showinfo(
            'Lab3', 'Варіант 17. Крапка, лінія, прямокутник, еліпс.\n'
            'Прямокутник: від центру до кута. Еліпс: два кути.\n'
            'Ліва кнопка — малювання; Esc — скасування.', parent=self.root)

    def point(self, event):
        return (max(0, min(event.x, self.canvas.winfo_width()-1)),
                max(0, min(event.y, self.canvas.winfo_height()-1)))

    def press(self, event):
        if self.editor.count >= N:
            messagebox.showwarning('Ліміт', 'Досягнуто межі 117 об’єктів. Очистіть полотно.',
                                   parent=self.root)
            return
        self.canvas.focus_set()
        self.start = self.point(event)
        self.move(event)

    def move(self, event):
        if self.start is None:
            return
        x, y = self.point(event)
        self.preview = SHAPE_TYPES[self.kind.get()](*self.start, x, y)
        self.redraw()

    def release(self, event):
        if self.start is None:
            return
        self.move(event)
        self.editor.add(self.preview)
        self.start = None
        self.preview = None
        self.redraw()

    def cancel(self, event=None):
        self.start = None
        self.preview = None
        self.redraw()

    def focus_out(self, event):
        if event.widget == self.canvas:
            self.cancel()

    def clear(self):
        self.editor.clear()
        self.cancel()

    def redraw(self):
        self.canvas.delete('all')
        self.editor.show(self.canvas)
        if self.preview is not None:
            self.preview.show(self.canvas, preview=True)
        self.status.set(f'Об’єктів: {self.editor.count}/{N}  |  Ліва кнопка — малювання; Esc — скасування')


if __name__ == '__main__':
    window = tk.Tk()
    Application(window)
    window.mainloop()
