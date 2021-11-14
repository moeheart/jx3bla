# Created by moeheart at 04/21/2021
# 分锅界面中的表格生成库。
# 使用tkinter的方法，在给定的frame中生成表格形式的内容。未来还会实现排序功能。

import tkinter as tk

from tools.Functions import getColor
from replayer.TableConstructor import TableConstructor
from replayer.occ.XiangZhi import XiangZhiProWindow
from replayer.occ.LingSu import LingSuWindow


class TableConstructorMeta(TableConstructor):
    '''
    元表格生成库，允许在生成表格时套用其它依赖表格的类，防止循环引用
    '''

    def GenerateXinFaReplayButton(self, xfResult, name):
        '''
        添加心法复盘按钮。
        '''
        if xfResult["occ"] == "22h":
            self.frame.occReplay[name] = XiangZhiProWindow(self.config, xfResult["result"])
            button = tk.Button(self.frame, text='相知', height=1, command=self.frame.occReplay[name].start, bg=getColor("22"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] == "212h":
            self.frame.occReplay[name] = LingSuWindow(self.config, xfResult["result"])
            button = tk.Button(self.frame, text='灵素', height=1, command=self.frame.occReplay[name].start, bg=getColor("212"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1

    def __init__(self, config, frame):
        super().__init__(config, frame)
