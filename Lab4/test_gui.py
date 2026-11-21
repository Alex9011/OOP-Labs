"""Інтеграційні тести Tkinter. Без дисплея позначаються як skipped."""
import gc
import tkinter as tk
import unittest
import weakref
from Lab4 import Application
from tools import TOOLS


class GuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f'Потрібен графічний дисплей: {exc}')
        self.errors = []
        self.root.report_callback_exception = self.callback_error
        self.app = Application(self.root)
        self.root.update()

    def callback_error(self, *args):
        self.errors.append(args)

    def tearDown(self):
        self.app.close()
        self.assertEqual(self.errors, [])

    def test_menu_toolbar_and_title(self):
        self.assertEqual(len(self.app.toolbar.buttons), 6)
        for i, tool in enumerate(TOOLS):
            self.app.objects_menu.invoke(i)
            self.root.update()
            self.assertEqual(self.app.editor.tool, tool.key)
            self.assertIn(tool.label, self.root.title())
            self.assertEqual(self.app.toolbar.buttons[tool.key]['relief'], 'sunken')
        for tool in TOOLS:
            self.app.toolbar.buttons[tool.key].invoke()
            self.assertEqual(self.app.kind.get(), tool.key)
            self.assertEqual(self.app.editor.tool, tool.key)

    def test_real_mouse_events_and_redraw(self):
        c = self.app.canvas
        for tool in TOOLS:
            self.app.toolbar.buttons[tool.key].invoke()
            c.event_generate('<ButtonPress-1>', x=150, y=150)
            c.event_generate('<B1-Motion>', x=220, y=240)
            self.root.update()
            preview = [i for i in c.find_all() if c.itemcget(i, 'dash')]
            self.assertTrue(preview)
            for i in preview:
                self.assertEqual(c.itemcget(i, 'dash'), '4 3')
            c.event_generate('<ButtonRelease-1>', x=220, y=240)
            self.root.update()
            self.assertFalse(any(c.itemcget(i, 'dash') for i in c.find_all()))
        self.assertEqual(self.app.editor.count, 6)
        self.root.geometry('1000x660')
        self.root.update()
        self.assertEqual(len(c.find_all()), 13)
        c.event_generate('<ButtonPress-1>', x=20, y=20)
        self.app.cancel()
        c.event_generate('<ButtonRelease-1>', x=80, y=80)
        self.assertEqual(self.app.editor.count, 6)
        self.app.clear()
        self.assertEqual(c.find_all(), ())

    def test_tooltip_timer_and_close(self):
        tip = self.app.toolbar.tooltips[-1]
        tip.widget.event_generate('<Enter>')
        self.root.after(650, self.root.quit)
        self.root.mainloop()
        self.assertIsNotNone(tip.window)
        self.assertTrue(tip.window.winfo_exists())
        tip.widget.event_generate('<Leave>')
        self.assertIsNone(tip.window)
        tip.OnNotify()
        reference = weakref.ref(self.app.editor)
        self.app.close()
        gc.collect()
        self.assertIsNone(reference())
        self.assertIsNone(tip.timer)
        self.app.close()


if __name__ == '__main__':
    unittest.main()
