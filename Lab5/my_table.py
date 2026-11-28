"""Немодальна таблиця з повідомленнями через callback-функції."""
import tkinter as tk
from tkinter import ttk


class MyTable:
    COLUMNS = ('Назва', 'x1', 'y1', 'x2', 'y2')

    def __init__(self, parent, on_select, on_delete, on_close):
        self.parent = parent
        self.on_select = on_select
        self.on_delete = on_delete
        self.on_close = on_close
        self.window = None
        self.tree = None

    @property
    def is_open(self):
        return self.window is not None

    def show(self):
        if self.is_open:
            self.window.lift()
            return
        self.window = tk.Toplevel(self.parent)
        self.window.title('Таблиця графічних об’єктів')
        self.window.minsize(420, 200)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        frame = ttk.Frame(self.window, padding=8)
        frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frame, columns=self.COLUMNS,
                                 show='headings', selectmode='browse', height=8)
        for i, title in enumerate(self.COLUMNS):
            self.tree.heading(title, text=title)
            self.tree.column(title, width=180 if i == 0 else 60,
                             minwidth=110 if i == 0 else 45,
                             anchor='w' if i == 0 else 'center')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll.grid(row=0, column=1, sticky='ns')
        self.delete_button = ttk.Button(frame, text='Видалити вибрану фігуру',
                                        command=self._delete, state='disabled')
        self.delete_button.grid(row=1, column=0, sticky='w', pady=(8, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.tree.bind('<<TreeviewSelect>>', self._select)
        self.tree.bind('<Delete>', self._delete)

    def refresh(self, rows, selected):
        if not self.is_open:
            return
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        for index, row in enumerate(rows):
            self.tree.insert('', 'end', iid=str(index), values=row)
        if selected is not None:
            iid = str(selected)
            self.tree.selection_set(iid)
            self.tree.focus(iid)
            self.tree.see(iid)
        self._update_button(selected)

    def _selected_index(self):
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

    def _update_button(self, index):
        self.delete_button.configure(state='disabled' if index is None else 'normal')

    def _select(self, event=None):
        index = self._selected_index()
        self._update_button(index)
        self.on_select(index)

    def _delete(self, event=None):
        index = self._selected_index()
        if index is not None:
            self.on_delete(index)

    def close(self):
        if self.is_open:
            self.window.destroy()
            self.window = self.tree = None
            self.on_close()
