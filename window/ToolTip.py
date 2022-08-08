# Created by moeheart at 08/08/2022
# 浮动标签类.

import tkinter as tk

class ToolTip(object):
    '''
    浮动标签类，用于实现简单的浮动标签。
    '''

    def build(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        tf = tk.Frame(tw, relief=tk.SOLID, borderwidth=1, bg="#ffffe0")
        tf.pack(ipadx=1)

        textList = text.split('\n')

        for line in textList:
            if line == "":
                fg = "#000000"
            if line[0] == "-":
                fg = "#ff0000"
            elif line[0] == "+":
                fg = "#007700"
            else:
                fg = "#000000"
            label = tk.Label(tf, text=line, fg=fg, justify=tk.LEFT,
                             background="#ffffe0", anchor='nw',
                             font=("Aaril", "10", "normal"))
            label.pack(anchor=tk.NW)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def createToolTip(self, widget, text):
        toolTip = self.build(widget)

        def enter(event):
            self.showtip(text)

        def leave(event):
            self.hidetip()

        self.widget = widget
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def remove(self):
        self.widget.unbind('<Enter>')
        self.widget.unbind('<Leave>')

    def __init__(self, widget, text):
        self.createToolTip(widget, text)