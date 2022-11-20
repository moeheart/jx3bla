# Created by moeheart at 04/21/2021
# 分锅界面中的表格生成库。
# 使用tkinter的方法，在给定的frame中生成表格形式的内容。未来还会实现排序功能。

import tkinter as tk

from tools.Functions import getColor
from replayer.TableConstructor import TableConstructor
from replayer.occ.XiangZhi import XiangZhiProWindow
from replayer.occ.LingSu import LingSuWindow
from replayer.occ.LiJingYiDao import LiJingYiDaoWindow
from replayer.occ.YunChangXinJing import YunChangXinJingWindow
from replayer.occ.BuTianJue import BuTianJueWindow
from window.DpsDisplayWindow import DpsDisplayWindow
from Constants import *

class TableConstructorMeta(TableConstructor):
    '''
    元表格生成库，允许在生成表格时套用其它依赖表格的类，防止循环引用
    '''

    def GenerateXinFaReplayButton(self, xfResult, name):
        '''
        添加心法复盘按钮。
        '''
        if xfResult["occ"] == "22h":
            self.frame.occReplay[name] = XiangZhiProWindow(self.config, xfResult)
            button = tk.Button(self.frame, text='相知', height=1, command=self.frame.occReplay[name].start, bg=getColor("22"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] == "212h":
            self.frame.occReplay[name] = LingSuWindow(self.config, xfResult)
            button = tk.Button(self.frame, text='灵素', height=1, command=self.frame.occReplay[name].start, bg=getColor("212"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] == "2h":
            self.frame.occReplay[name] = LiJingYiDaoWindow(self.config, xfResult)
            button = tk.Button(self.frame, text='离经易道', height=1, command=self.frame.occReplay[name].start, bg=getColor("2"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] == "5h":
            self.frame.occReplay[name] = YunChangXinJingWindow(self.config, xfResult)
            button = tk.Button(self.frame, text='云裳心经', height=1, command=self.frame.occReplay[name].start, bg=getColor("5"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] == "6h":
            self.frame.occReplay[name] = BuTianJueWindow(self.config, xfResult)
            button = tk.Button(self.frame, text='补天诀', height=1, command=self.frame.occReplay[name].start, bg=getColor("6"))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1
        elif xfResult["occ"] in ["1d", "1t", "2d", "3d", "3t", "4p", "4m", "5d", "6d", "7p", "7m", "8", "9", "10d", "10t",
                                          "21d", "21t", "22d", "23", "24", "25", "211", "212d", "213"]:  # 所有的DPS
            self.frame.occReplay[name] = DpsDisplayWindow(self.config, xfResult)
            button = tk.Button(self.frame, text=OCC_PINYIN_DICT[xfResult["occ"]], height=1, command=self.frame.occReplay[name].start, bg=getColor(xfResult["occ"]))
            button.grid(row=self.nowx, column=self.nowy)
            self.nowy += 1

    def __init__(self, config, frame):
        super().__init__(config, frame)
