"""Lab5, варіант 16. Запуск: python Lab5.py."""
import tkinter as tk
from csv import Error as CsvError
from tkinter import filedialog, messagebox
from editor import MyEditor, CAPACITY
from my_table import MyTable
from shape_csv import load_shapes, save_shapes
from tools import TOOLS, TOOL_BY_CLASS, TOOL_BY_KEY
from toolbar import ShapeToolbar

CSV_FILTER = [('CSV', '*.csv'), ('Усі файли', '*.*')]

class Application:
    def __init__(self, root):
        self.root = root
        self.editor = MyEditor.instance()
        self._closed = False
        self._selected = None
        self.kind = tk.StringVar(master=root, value='point')
        root.geometry('960x620')
        root.minsize(640, 420)
        root.protocol('WM_DELETE_WINDOW', self.close)
        bar = tk.Menu(root, tearoff=False)
        file_menu = tk.Menu(bar, tearoff=False)
        file_menu.add_command(label='Відкрити CSV…', command=self.open_file)
        file_menu.add_command(label='Зберегти CSV…', command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label='Очистити', command=self.clear)
        file_menu.add_separator()
        file_menu.add_command(label='Вихід', command=self.close)
        bar.add_cascade(label='Файл', menu=file_menu)
        self.objects_menu = tk.Menu(bar, tearoff=False)
        for tool in TOOLS:
            self.objects_menu.add_radiobutton(
                label=tool.label, variable=self.kind, value=tool.key,
                command=self.select_shape)
        bar.add_cascade(label='Об’єкти', menu=self.objects_menu)
        self.table = MyTable(root, self.select_row, self.delete_row, self.table_closed)
        self.view_menu = tk.Menu(bar, tearoff=False)
        self.view_menu.add_command(label='Відкрити таблицю', command=self.toggle_table)
        bar.add_cascade(label='Вигляд', menu=self.view_menu)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label='Про програму', command=self.about)
        bar.add_cascade(label='Довідка', menu=help_menu)
        root.config(menu=bar)
        self.toolbar = ShapeToolbar(root, self.kind, self.select_shape)
        self.toolbar.pack(side='top', fill='x')
        self.status = tk.StringVar(master=root)
        tk.Label(root, textvariable=self.status, anchor='w').pack(
            side='bottom', fill='x')
        self.canvas = tk.Canvas(root, background='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<ButtonPress-1>', self.press)
        self.canvas.bind('<B1-Motion>', self.move)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<Configure>', self.configure)
        self.canvas.bind('<FocusOut>', self.cancel)
        root.bind('<Escape>', self.cancel)
        self.select_shape()

    def select_shape(self):
        self.editor.select(self.kind.get())
        self.toolbar.sync()
        label = TOOL_BY_KEY[self.editor.tool].label
        self.root.title(f'Lab5 — Варіант 16 — {label}')
        self.redraw()

    def point(self, event):
        return (max(0, min(event.x, self.canvas.winfo_width()-1)),
                max(0, min(event.y, self.canvas.winfo_height()-1)))

    def press(self, event):
        self.canvas.focus_set()
        if not self.editor.begin(*self.point(event)):
            messagebox.showwarning('Ліміт',
                f'Досягнуто межі {CAPACITY} об’єктів. Очистіть полотно.',
                parent=self.root)
        self.redraw()

    def move(self, event):
        self.editor.update(*self.point(event))
        self.redraw()

    def release(self, event):
        if self.editor.finish(*self.point(event)):
            self.refresh_table()
        self.redraw()

    def cancel(self, event=None):
        if not self._closed:
            self.editor.cancel()
            self.redraw()

    def clear(self):
        self.editor.clear()
        self._selected = None
        self.refresh_table()
        self.redraw()

    def toggle_table(self):
        if self.table.is_open:
            self.table.close()
        else:
            self.table.show()
            self.view_menu.entryconfigure(0, label='Закрити таблицю')
            self.refresh_table()

    def table_closed(self):
        self._selected = None
        if not self._closed:
            self.view_menu.entryconfigure(0, label='Відкрити таблицю')
            self.redraw()

    def refresh_table(self):
        if self.table.is_open:
            rows = [(TOOL_BY_CLASS[type(shape)].label, *shape.coords)
                    for shape in self.editor.shapes]
            self.table.refresh(rows, self._selected)

    def select_row(self, index):
        if index != self._selected:
            self._selected = index
            self.redraw()

    def delete_row(self, index):
        if self.editor.remove(index):
            self._selected = None
            self.refresh_table()
            self.redraw()

    def open_file(self):
        path = filedialog.askopenfilename(parent=self.root, filetypes=CSV_FILTER)
        if not path:
            return
        if self.editor.count and not messagebox.askyesno(
                'Відкрити CSV', 'Замінити поточні фігури фігурами з файлу?',
                parent=self.root):
            return
        try:
            self.editor.replace(load_shapes(path))
        except (OSError, ValueError, CsvError) as error:
            messagebox.showerror('Не вдалося відкрити CSV', str(error), parent=self.root)
            return
        self._selected = None
        self.refresh_table()
        self.redraw()

    def save_file(self):
        path = filedialog.asksaveasfilename(
            parent=self.root, filetypes=CSV_FILTER, defaultextension='.csv')
        if path:
            try:
                save_shapes(path, self.editor.shapes)
            except OSError as error:
                messagebox.showerror('Не вдалося зберегти CSV', str(error), parent=self.root)

    def configure(self, event):
        self.redraw()

    def redraw(self):
        if self._closed:
            return
        self.canvas.delete('all')
        self.editor.Show(self.canvas, self._selected)
        self.status.set(f'Об’єктів: {self.editor.count}/{CAPACITY}  |  '
                        'Ліва кнопка — малювання; Esc — скасування')

    def about(self):
        messagebox.showinfo('Lab5',
            'Варіант 16. Шість фігур, пунктирний гумовий слід.\n'
            'Прямокутник: центр → кут. Еліпс: два кути.\n'
            'Куб: перетягніть діагональ передньої квадратної грані.\n'
            'Кружечки розташовані на кінцях лінії.\n'
            'Вигляд → Відкрити таблицю. Файл → Зберегти або відкрити CSV.',
            parent=self.root)

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.table.close()
            self.toolbar.dispose()
        finally:
            self.editor.close()
            self.editor = None
            self.root.destroy()


def main():
    root = tk.Tk()
    app = None
    try:
        app = Application(root)
        root.mainloop()
    finally:
        if app is not None:
            app.close()
        else:
            # Прибираємо Singleton, якщо ініціалізація вікна не завершилася.
            MyEditor.instance().close()
            root.destroy()


if __name__ == '__main__':
    main()
