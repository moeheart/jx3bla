# Created by moeheart at 01/22/2023
# 花间游的复盘方法。

from replayer.occ.Dps import DpsReplayer

from replayer.BattleHistory import BattleHistory, SingleSkill
from tools.Names import *
from tools.Functions import *
from replayer.Name import *
from window.DpsDisplayWindow import DpsDisplayWindow, SingleSkillDisplayer

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk

import webbrowser

import time

class HuaJianYouWindow(DpsDisplayWindow):
    '''
    花间复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''这里显示一些说明的情况'''
        messagebox.showinfo(title='说明', message=text)

    def openHelp(self):
        '''
        打开心法的介绍网页.暂借一下花椒油的
        '''
        url = "https://www.jx3box.com/bps/56562"
        webbrowser.open(url)

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - config: 设置类
        - result: 花间复盘的结果.
        '''
        super().__init__(config, result)
        self.setThemeColor("#A655FB")
        self.title = '衍天复盘'
        self.occ = "taixuanjing"

class HuaJianYouReplayer(DpsReplayer):
    '''
    艳艳复盘类。
    '''


    # def calculateSkillInfoDirect(self, name, skillObj):
    #     '''
    #     根据技能名和对象统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - skillObj: skillInfo中定义的技能对象.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))
    #
    # def calculateSkillInfo(self, name, id):
    #     '''
    #     根据技能名和ID统计对应技能的基本信息.
    #     注意更复杂的信息依然需要在派生类中手动统计.
    #     params:
    #     - name: 技能的简称. 会存储在result中.
    #     - id: 技能的ID，用于在skillInfo中查找.
    #     returns:
    #     - skillObj: 查找到的技能对象，用于进一步的手动统计.
    #     '''
    #     skillObj = self.skillInfo[self.gcdSkillIndex[id]][0]
    #     self.result["skill"][name] = {}
    #     self.result["skill"][name]["num"] = skillObj.getNum()
    #     self.result["skill"][name]["numPerSec"] = roundCent(self.result["skill"][name]["num"] / self.result["overall"]["sumTimeEff"] * 1000, 2)
    #     self.result["skill"][name]["delay"] = int(skillObj.getAverageDelay())
    #     effHeal = skillObj.getHealEff()
    #     self.result["skill"][name]["HPS"] = int(effHeal / self.result["overall"]["sumTimeEff"] * 1000)
    #     self.result["skill"][name]["effRate"] = roundCent(safe_divide(effHeal, skillObj.getHeal()))



    def replay(self):
        '''
        开始复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", actorData={}):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - myname: 需要复盘的奶歌名.
        - actorData: 演员复盘得到的统计记录.
        '''
        super().__init__(config, fileNameInfo, path, bldDict, window, myname, actorData)
        self.public = 1  # 暂时强制公开，反正没什么东西  TODO 更改设置中的选项，简化内容
        self.myname = myname
        self.occ = "taixuanjing"
        self.occCode = "211"
        self.occPrint = "衍天"
        self.occColor = getColor(self.occCode)