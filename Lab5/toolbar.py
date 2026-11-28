"""Панель іконок і спливаючі підказки. Усі обробники — методи класів."""
import tkinter as tk
from pkgutil import get_data
from tools import TOOLS


class ToolTip:
    def __init__(self, widget, text):
        self.widget, self.text = widget, text
        self.timer = None
        self.window = None
        widget.bind('<Enter>', self.OnNotify, add='+')
        widget.bind('<Leave>', self.hide, add='+')
        widget.bind('<ButtonPress-1>', self.hide, add='+')
        widget.bind('<Destroy>', self.hide, add='+')

    def OnNotify(self, event=None):
        # Аналог повідомлення про наведення, а не нативний WM_NOTIFY.
        self.hide()
        self.timer = self.widget.after(500, self.show)

    def show(self):
        self.timer = None
        self.window = tk.Toplevel(self.widget)
        self.window.overrideredirect(True)
        tk.Label(self.window, text=self.text, background='#fffbd6',
                 relief='solid', borderwidth=1, padx=6, pady=4).pack()
        self.window.update_idletasks()
        x = min(self.widget.winfo_rootx(),
                self.widget.winfo_screenwidth()-self.window.winfo_width())
        y = self.widget.winfo_rooty()+self.widget.winfo_height()+4
        self.window.geometry(f'+{max(0, x)}+{y}')

    def hide(self, event=None):
        if self.timer is not None:
            self.widget.after_cancel(self.timer)
            self.timer = None
        if self.window is not None:
            self.window.destroy()
            self.window = None


class ShapeToolbar(tk.Frame):
    def __init__(self, parent, variable, command):
        super().__init__(parent, relief='raised', borderwidth=1)
        self.variable = variable
        self.images, self.buttons, self.tooltips = {}, {}, []
        for tool in TOOLS:
            name, filename = tool.key, tool.icon
            image = tk.PhotoImage(master=self,
                                  data=get_data(__name__, f'assets/{filename}'))
            self.images[name] = image  # Зберігаємо посилання на зображення.
            button = tk.Radiobutton(
                self, image=image, variable=variable, value=name,
                indicatoron=False, command=command, width=36, height=34,
                selectcolor='#cde5ff', relief='flat', borderwidth=2)
            button.pack(side='left', padx=2, pady=2)
            self.buttons[name] = button
            self.tooltips.append(ToolTip(button, tool.label))
        self.sync()

    def sync(self):
        for name, button in self.buttons.items():
            button.configure(relief='sunken' if
                             self.variable.get() == name else 'flat')

    def dispose(self):
        for tooltip in self.tooltips:
            tooltip.hide()
