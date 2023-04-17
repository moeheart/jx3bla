# Created by moeheart at 04/15/2022
# 武云阙的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class WuYunqueWindow(SpecificBossWindow):
    '''
    武云阙的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("武云阙", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        # tb.AppendHeader("本体DPS", "对张景超的DPS。\n常规阶段时间：%s" % parseTime(self.detail["P1Time"]))
        # tb.AppendHeader("双体1DPS", "第一次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time1"]))
        # tb.AppendHeader("双体2DPS", "第二次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time2"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class WuYunqueReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        # self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        # self.detail["P2Time1"] = int(self.phaseTime[2] / 1000)
        # self.detail["P2Time2"] = int(self.phaseTime[3] / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                res = self.getBaseList(id)
                bossResult.append(res)
        self.statList = bossResult

        return self.statList, self.potList, self.detail, self.stunCounter

    def recordDeath(self, item, deathSource):
        '''
        在有玩家重伤时的额外代码。
        params
        - item 复盘数据，意义同茗伊复盘。
        - deathSource 重伤来源。
        '''
        pass

    def analyseSecondStage(self, event):
        '''
        处理单条复盘数据时的流程，在第二阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''

        self.checkTimer(event.time)

        if event.dataType == "Skill":
            if event.target in self.bld.info.player:
                if event.heal > 0 and event.effect != 7 and event.caster in self.hps:  # 非化解
                    self.hps[event.caster] += event.healEff

                if event.caster in self.bld.info.npc and event.heal == 0 and event.scheme == 1:
                    # 尝试记录技能事件
                    name = "s%s" % event.id
                    if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                        self.bhTime[name] = event.time
                        skillName = self.bld.info.getSkillName(event.full_id)
                        if "," not in skillName:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["武云阙"]:
                            self.bh.setMainTarget(event.target)

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

        elif event.dataType == "Shout":
            if event.content in ['"来人！助我一臂之力！"']:
                self.bh.setEnvironment("0", "武家弟子", "1118", event.time, 0, 1, "NPC出现", "shout", "#000000")
            elif event.content in ['"阴雨连绵！"']:
                pass
            elif event.content in ['"情况不妙！我们先撤！"']:
                pass
            elif event.content in ['"嘿！呀！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"雕虫小技！"']:
                pass
            elif event.content in ['"疾风枭首！"', '"疾風梟首！"']:
                pass
            elif event.content in ['"无处可逃！"']:
                pass
            elif event.content in ['"哼，我才不会死在你们手里！"', '"哼，我才不會死在你們手裏！"']:
                pass
            elif event.content in ['"哼!"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["张景超宝箱", "張景超寶箱"]:
            #     self.win = 1
            #     self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                                               1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            pass

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 2000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式开始运功", "cast")

                    
    def analyseFirstStage(self, item):
        '''
        处理单条复盘数据时的流程，在第一阶段复盘时，会以时间顺序不断调用此方法。
        params
        - item 复盘数据，意义同茗伊复盘。
        '''
        pass

    def initBattle(self):
        '''
        在战斗开始时的初始化流程，当第二阶段复盘开始时运行。
        '''
        self.initBattleBase()
        self.activeBoss = "武云阙"

        self.initPhase(1, 1)

        self.bhBlackList.extend(["s34891", "s34614", "n122382", "s34411", "s34414", "b25744", "b25745", "b26164",
                                 "s34407", "n122403", "n122594", "n122236", "n122494", "c34409", "s34410", "n122546",
                                 "n122242", "s34641", "b25781", "s34893", "s34621", "s34413", "n122550", "n112055"
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       # "c31145": ["3452", "#773333", 2000],  # 迅风裂
                       # "c31102": ["4224", "#ff7700", 5000],  # 疾雷
                       # "c31152": ["3408", "#7700ff", 5000],  # 刀止横流
                       # "c31148": ["4564", "#00ffff", 0],  # 绝风疾
                       # "c31260": ["4222", "#ff7777", 5000],  # 万钧
                       # "c31328": ["2146", "#ff77cc", 7000],  # 逆闪
                       # "c31851": ["3434", "#ff77ff", 7000],  # 霆鸣
                       # "c33130": ["2028", "#ff0000", 20000],  # 风雷灭尽
                       "c34411": ["2024", "#ff0000", 3000],  # 大戮戟法·峰回
                       "c34414": ["3399", "#ff7700", 2000],  # 大戮戟法·唤风
                       "c34408": ["2019", "#0000ff", 12000],  # 大戮戟法·怒舞
                       "c34639": ["2033", "#7777ff", 3000],  # 连绵阴雨针
                       "c34620": ["2034", "#7700ff", 3000],  # 连绵阴雨针
                       "c34412": ["13167", "#0077ff", 3000],  # 大戮戟法·定虚




                       }

        # 武云阙数据格式：
        # 7 ？

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

