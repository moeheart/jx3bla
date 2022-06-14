# Created by moeheart at 04/21/2021
# 分锅界面中的表格生成库。
# 使用tkinter的方法，在给定的frame中生成表格形式的内容。未来还会实现排序功能。

import tkinter as tk

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
 
        self.label = tk.Label(tw, text=text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("Aaril", "10", "normal"))
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
        self.widget = widget
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def remove(self):
        self.widget.unbind('<Enter>')
        self.widget.unbind('<Leave>')
        
    def __init__(self, widget, text):
        self.createToolTip(widget, text)

class TableConstructor():
    '''
    表格生成库。
    '''
    
    def EndOfLine(self):
        '''
        为表格换行。
        '''
        if self.nowx == 0:
            self.width = self.nowy
        self.nowx += 1
        self.nowy = 0
    
    def AppendContext(self, text, color=None, width=None, justify=None):
        '''
        添加表格内容。
        '''
        label = tk.Label(self.frame, text=text, width=width, fg=color, justify=justify)
        label.grid(row=self.nowx, column=self.nowy)
        self.nowy += 1
    
    def AppendHeader(self, text, hint, width=None, color=None):
        '''
        添加标题栏。
        '''
        label = tk.Label(self.frame, text=text, width=width, height=1, fg=color)
        label.grid(row=self.nowx, column=self.nowy)
        self.nowy += 1
        if hint != "":
            ToolTip(label, hint)
    
    def __init__(self, config, frame):
        self.frame = frame
        self.config = config
        self.nowx = 0
        self.nowy = 0
        self.width = 0
        self.frame.occReplay = {}

