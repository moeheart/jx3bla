import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from PIL import Image
import re
import os
import time

class ToolTip(object):
    def __init__(self, widget):
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
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
 
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("Aaril", "8", "normal"))
        label.pack(ipadx=1)
 
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

window = tk.Tk()
window.title('test')
window.geometry('300x200')

l = tk.Label(window, text='文本', width=30, height=1)
l.pack()

b1 = tk.Button(window, text='按钮', bg='#ccffcc', width=12, height=1)
b1.pack()

createToolTip(l, '你知道的太多了')
createToolTip(b1, '你知道的太多了\n两行！')

window.mainloop()



