# coding: utf-8
import os
import threading

from am.am_parser import am_from_string
from am.commands import cmd
from am.commands.graph import get_dot


@cmd(require_file=False)
def designer(filename, *args, **kwargs):
    """
    Interactive automatic machine editor with live preview. Requires Graphviz.
    """
    import tkinter as tk
    from tkinter import ttk
    import idlelib.colorizer as ic
    import idlelib.percolator as ip
    import re
    import json
    from collections import defaultdict
    class Editor(tk.Text):
        def __init__(self, parent, handler):
            super().__init__(parent)
            cdg = ic.ColorDelegator()
            with open(pathlib.Path(__file__).parent.parent.parent.parent / "plugins/language-automatic-machines-simulator/grammars/automatic-machines-simulator.json") as fp:
                rules = json.load(fp)
            regex = defaultdict(lambda: [])
            def esc(x):
                return repr(x)[1:-1]
            for name, elem in rules["repository"].items():
                if not (p := elem.get("patterns", [None])[0]):
                    p = elem
                category, *rest = p["name"].split(".")
                if not (match := p.get("match")):
                    begin = p["begin"]
                    end = p["end"]
                    match = esc(begin) + r"[^" + esc(end) + "]*" + esc(end)
                regex[category].append(match)
            cdg.prog = re.compile("|".join(r'(?P<' + category.upper() + '>' + "|".join(f"({x})" for x in expr) + r')' for category, expr in regex.items())
                                  + r"|(?P<SYNC>\n)", re.S)
            cdg.idprog = re.compile(r'\s+(\w+)', re.S)
            cdg.tagdefs["VARIABLE"] = cdg.tagdefs["DEFINITION"]
            cdg.tagdefs['MYGROUP'] = {'foreground': '#7F7F7F', 'background': '#FFFFFF'}
            ip.Percolator(self).insertfilter(cdg)
            self.handler = handler
            self.configure(font='TkFixedFont')
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

    import pathlib

    import pydot
    from PIL import Image, ImageTk
    import io

    dot_code = None
    ev = threading.Event()
    exited = False
    def runner():
        while True:
            ev.wait(1)
            if exited:
                return
            if not ev.is_set():
                continue
            ev.clear()
            try:
                graph, = pydot.graph_from_dot_data(dot_code)
            except:
                print(dot_code)
            else:
                image = Image.open(io.BytesIO(graph.create_png()))
                disp = ImageTk.PhotoImage(image)
                b2.configure(image=disp, width=disp.width(), height=disp.height())
                b2.image = disp

    thr = threading.Thread(target=runner)

    old_drop = None

    def text_changed(event):
        nonlocal old_drop
        code = b1.get("1.0", "end-1c")
        try:
            res = am_from_string(code)
            mac_names = {x.name: x for x in res}
            drop["values"] = list(mac_names.keys())
            if len(mac_names) == 1 or drop.get() not in mac_names:
                drop.current(0)
            machine = mac_names[drop.get()]
            if drop.get() != old_drop:
                b1.see(str(machine.lineno) + ".0")
            nonlocal dot_code
            old_drop = drop.get()
            dot_code = get_dot(machine, True, True).replace("label = ", "label =")
            ev.set()
        except:
            pass


    b1 = Editor(root, text_changed)
    if filename:
        try:
            with open(filename, "r", encoding="utf-8") as fp:
                b1.insert(1.0, fp.read())
        except:
            pass
    b1.grid(column=0, row=0, sticky="nsew")

    fright = tk.Frame(root)
    fright.grid(column=1, row=0, sticky="nsew")
    fright.grid_columnconfigure(0, weight=1)
    fright.grid_rowconfigure(1, weight=1)
    drop = ttk.Combobox(fright, values=["Choisissez une machine"])
    drop.current(0)
    drop.grid(column=0, row=0, sticky="ew")
    drop.bind("<<ComboboxSelected>>", text_changed)
    b2 = tk.Label(fright, width=50)
    b2.grid(column=0, row=1, sticky="nsew")
    root.grid_columnconfigure(0, weight=1, uniform="group1")
    root.grid_columnconfigure(1, weight=2, uniform="group1")
    root.grid_rowconfigure(0, weight=1)

    thr.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

    os._exit(0)
