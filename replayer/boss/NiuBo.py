# Created by moeheart at 04/15/2022
# 牛波的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class NiuBoWindow(SpecificBossWindow):
    '''
    牛波的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("牛波", "1200x800")
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

class NiuBoReplayer(SpecificReplayerPro):

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

        if self.EHuDisappear != 0 and event.time - self.EHuDisappear > 30000:
            self.bh.setBadPeriod(self.EHuDisappear, event.time, True, True)

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
                        if self.bld.info.getName(event.target) in ["牛波"]:
                            self.bh.setMainTarget(event.target)

            if event.id == "34364":
                if self.EHuDisappear != 0:
                    self.bh.setBadPeriod(self.EHuDisappear, event.time, True, True)
                    self.EHuDisappear = 0

            # if self.bld.info.getName(event.caster) == "恶虎":
            #     print("[EHuTest]", event.time, parseTime((event.time - self.startTime) / 1000), event.id,
            #           (self.bld.info.getSkillName(event.full_id)), self.bld.info.getName(event.target), event.damage, event.damageEff)

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

            # if self.bld.info.getSkillName(event.full_id) in ["云生结海", "盾壁"]:
            #     print("[YunShengTest]", event.time, parseTime((event.time - self.startTime) / 1000), event.id,
            #            self.bld.info.getName(event.target), event.stack)



        elif event.dataType == "Shout":
            if event.content in ['"哼……"']:
                pass
            elif event.content in ['"尝尝这个！"']:
                pass
            elif event.content in ['"出来吧！到你了！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "黑熊登场", "shout", "#333333")
            elif event.content in ['"给我死！"']:
                pass
            elif event.content in ['"喝啊！"']:
                pass
            elif event.content in ['"呼噜……"']:
                pass
            elif event.content in ['"该你上场了！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "恶虎登场", "shout", "#333333")
            elif event.content in ['"你们这群废物！亏我天天毫不吝啬的喂养你们！真是一点用都没有！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"都给老子……啊？啊啊啊啊啊啊……"']:
                pass
            elif event.content in ['"很痛吗？嘿嘿嘿！痛就对了！"']:
                pass
            elif event.content in ['"啊啊啊啊！"']:
                pass
            elif event.content in ['"睡吧~睡吧！"']:
                pass
            elif event.content in ['"畜生们，准备好！"']:
                pass
            elif event.content in ['"开饭咯！"']:
                pass
            elif event.content in ['"咕~~~（似乎是肚子发出的声音）"']:
                pass
            elif event.content in ['"呃！什么？"']:
                pass
            elif event.content in ['"你这畜生！是那边！"']:
                pass
            elif event.content in ['"去吧！碾碎他们！"']:
                pass
            elif event.content in ['"去吧！碾碎他们！"']:
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
            if event.id in self.bld.info.npc and not event.enter and self.bld.info.getName(event.id) in ["恶虎"]:
                self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, "恶虎消失", "340", event.time, 0,
                                       1, "隐袭阶段开始", "npc")
                self.EHuDisappear = event.time

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
        self.activeBoss = "牛波"

        self.initPhase(1, 1)

        self.bhBlackList.extend(["s34366", "b25719", "s34146", "n122498", "s34333", "s34337", "n122486", "n122510",
                                 "s34368", "s34365", "n122582", "n122561", "s34330", "c34336", "s34335", "s34332",
                                 "s34358", "n122477", "b25720", "n122492", "n122552", "n122550", "n122984", "n122624",
                                 "b25644", "b25635", "s34150", "b25636", "n122610", "n122907", "n122604", "b25729",
                                 "s34384", "b25737", "b25700", "s34376", "n122603", "s34377", "b25730"


                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       # "c31145": ["3452", "#773333", 2000],  # 迅风裂
                       "c34178": ["3426", "#0000ff", 3000],  # 钉刺重锤
                       "s34180": ["3428", "#ff0000", 0],  # 刺刃环芒
                       "c34338": ["2019", "#0077ff", 7000],  # 撕咬
                       "s34149": ["3445", "#ff7700", 0],  # 黑恶怒吼
                       "c34332": ["3293", "#00ff00", 0],  # 翼击
                       "c34334": ["3293", "#00ff00", 0],  # 站立扑击
                       "s34364": ["2028", "#7700ff", 0],  # 隐袭
                       "s34151": ["397", "#ff77ff", 0],  # 麻醉弩箭
                       "c34245": ["128", "#ff0077", 5000],  # 饲料诱饵
                       "c34376": ["2031", "#ff77cc", 3000],  # 象足撼地
                       "c34379": ["345", "#007700", 0],  # 象鼻音波
                       }

        # 牛波数据格式：
        # 7 ？
        self.EHuDisappear = 0

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

