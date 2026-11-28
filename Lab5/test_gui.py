"""Інтеграційні тести Tkinter. Без дисплея позначаються як skipped."""
import gc
import tempfile
import tkinter as tk
import unittest
import weakref
from pathlib import Path
from unittest.mock import patch
from Lab5 import Application
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

    def test_table_is_nonmodal_and_synced(self):
        app = self.app
        app.view_menu.invoke(0)
        self.root.update()
        self.assertTrue(app.table.is_open)
        table_window = app.table.window
        self.assertIsNone(self.root.grab_current())
        for x in (100, 200):
            app.canvas.event_generate('<ButtonPress-1>', x=x, y=100)
            app.canvas.event_generate('<ButtonRelease-1>', x=x+10, y=125)
            self.root.update()
        tree = app.table.tree
        self.assertEqual(tree.get_children(), ('0', '1'))
        self.assertEqual(tuple(map(str, tree.item('0', 'values'))),
                         ('Крапка', '100', '100', '100', '100'))
        tree.selection_set('1')
        self.root.update()
        self.assertEqual(len(app.canvas.find_withtag('selection')), 1)
        highlight = app.canvas.coords(app.canvas.find_withtag('selection')[0])
        self.assertGreater(highlight[0], 180)
        app.table.delete_button.invoke()
        self.root.update()
        self.assertEqual(tree.get_children(), ('0',))
        self.assertEqual(app.editor.shapes[0].coords, (100, 100, 100, 100))
        self.assertEqual(app.canvas.find_withtag('selection'), ())
        app.view_menu.invoke(0)
        self.assertFalse(app.table.is_open)
        self.assertFalse(table_window.winfo_exists())
        app.view_menu.invoke(0)
        self.assertEqual(app.table.tree.get_children(), ('0',))
        table_window = app.table.window
        self.app.close()
        self.assertIsNone(app.table.window)
        self.assertIsNone(app.editor)

    def test_csv_menu_roundtrip_and_bad_file_preserves_scene(self):
        app = self.app
        file_menu = app.root.nametowidget(
            app.root.nametowidget(app.root['menu']).entrycget(0, 'menu'))
        app.toggle_table()
        app.canvas.event_generate('<ButtonPress-1>', x=40, y=30)
        app.canvas.event_generate('<ButtonRelease-1>', x=40, y=30)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'scene.csv'
            with patch('Lab5.filedialog.asksaveasfilename', return_value=str(path)):
                file_menu.invoke(1)
            self.assertTrue(path.is_file())
            app.clear()
            with patch('Lab5.filedialog.askopenfilename', return_value=str(path)):
                file_menu.invoke(0)
            self.root.update()
            self.assertEqual(app.table.tree.get_children(), ('0',))
            self.assertEqual(app.editor.shapes[0].coords, (40, 30, 40, 30))
            self.assertEqual(len(app.canvas.find_all()), 1)
            path.write_text('type,x1,y1,x2,y2\nwrong,10,20,30,40\n')
            with patch('Lab5.filedialog.askopenfilename', return_value=str(path)):
                with patch('Lab5.messagebox.askyesno', return_value=True):
                    with patch('Lab5.messagebox.showerror') as showerror:
                        file_menu.invoke(0)
                        showerror.assert_called_once()
            self.assertEqual(app.editor.shapes[0].coords, (40, 30, 40, 30))
            self.assertEqual(app.table.tree.get_children(), ('0',))


if __name__ == '__main__':
    unittest.main()
