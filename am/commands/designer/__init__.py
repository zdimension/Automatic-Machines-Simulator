# coding: utf-8
from am.am_parser import am_from_string
from am.commands import cmd
from am.commands.graph import get_dot


@cmd(require_file=False)
def designer(filename, *args, **kwargs):
    import tkinter as tk

    class Editor(tk.Text):
        def __init__(self, parent, handler):
            super().__init__(parent)
            self.handler = handler
            self._debounce = False
            self._clear_flag()
            self.bind('<<Modified>>', self._modified)

        def _modified(self, event=None):
            if self._debounce:
                self._debounce = False
                return
            if self._resetting_modified_flag: return
            self._clear_flag()
            self._debounce = True
            self.handler(event)

        def _clear_flag(self):
            self._resetting_modified_flag = True
            try:
                self.tk.call(self._w, 'edit', 'modified', 0)
            finally:
                self._resetting_modified_flag = False

    root = tk.Tk()

    import pydot
    from PIL import Image, ImageTk
    import io

    def text_changed(*args):
        code = b1.get("1.0", "end-1c")
        try:
            machine = am_from_string(code)[0]
            dot = get_dot(machine).replace("label = ", "label =")
           # print(dot)
            graph, = pydot.graph_from_dot_data(dot)
        except:
            pass
        else:
            image = Image.open(io.BytesIO(graph.create_png()))
            disp = ImageTk.PhotoImage(image)
            b2.configure(image=disp,width=disp.width(),height=disp.height())
            b2.image = disp
            #b2.pack()

    b1 = Editor(root, text_changed)
    if filename:
        try:
            with open(filename, "r") as fp:
                b1.insert(1.0, fp.read())
        except:
            pass
    b1.grid(column=0, row=0)
    b2 = tk.Label(root, width=50)
    b2.grid(column=1, row=0)

    if False:
        # Set the initial theme
        root.tk.call("source", "sun-valley.tcl")
        root.tk.call("set_theme", "light")

        def change_theme():
            # NOTE: The theme's real name is sun-valley-<mode>
            if root.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
                # Set light theme
                root.tk.call("set_theme", "light")
            else:
                # Set dark theme
                root.tk.call("set_theme", "dark")

        # Remember, you have to use ttk widgets
        button = ttk.Button(big_frame, text="Change theme!", command=change_theme)
        button.pack()

    root.mainloop()
