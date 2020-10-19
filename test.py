import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from PIL import Image
import re
import os
import time


class ToolTip(object):
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
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
 
        self.label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("Aaril", "8", "normal"))
        self.label.pack(ipadx=1)
 
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
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def modifyText(self, text):
        self.label.configure(text=text)
        
    def __init__(self, widget, text):
        self.createToolTip(widget, text)
        
window = tk.Tk()
window.title('test')
window.geometry('300x200')

canvas=tk.Canvas(window,width=550,height=500,scrollregion=(0,0,530,250)) #创建canvas
canvas.place(x = 25, y = 25) #放置canvas的位置
frame=tk.Frame(canvas) #把frame放在canvas里
frame.place(width=530, height=500) #frame的长宽，和canvas差不多的
vbar=tk.Scrollbar(canvas,orient=tk.VERTICAL) #竖直滚动条
vbar.place(x = 530,width=20,height=500)
vbar.configure(command=canvas.yview)
canvas.config(yscrollcommand=vbar.set) #设置  
canvas.create_window((265,125), window=frame)  #create_window


l = tk.Label(frame, text='文本', width=30, height=1)
l.pack()

b1 = tk.Button(frame, text='按钮', bg='#ccffcc', width=12, height=1)
b1.pack()



ToolTip(l, '你知道的太多了')
ToolTip(b1, '你知道的太多了\n两行！')

window.mainloop()



