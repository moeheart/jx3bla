# Created by moeheart at 11/03/2022
# 张景超&张法雷的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class ZhangJingchaoWindow(SpecificBossWindow):
    '''
    张景超&张法雷的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("张景超", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("本体DPS", "对张景超的DPS。\n常规阶段时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("双体1DPS", "第一次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time1"]))
        tb.AppendHeader("双体2DPS", "第二次内外场阶段，对张法雷（红色）和劲风（蓝色）的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time2"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["zjcDPS"]))
            if line["battle"]["zflDPS1"] > line["battle"]["jfDPS1"]:
                tb.AppendContext(int(line["battle"]["zflDPS1"]), color="#ff0000")
            else:
                tb.AppendContext(int(line["battle"]["jfDPS1"]), color="#0000ff")
            if line["battle"]["zflDPS2"] > line["battle"]["jfDPS2"]:
                tb.AppendContext(int(line["battle"]["zflDPS2"]), color="#ff0000")
            else:
                tb.AppendContext(int(line["battle"]["jfDPS2"]), color="#0000ff")

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class ZhangJingchaoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time1"] = int(self.phaseTime[2] / 1000)
        self.detail["P2Time2"] = int(self.phaseTime[3] / 1000)

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.statDict:
                # line = self.stat[id]
                res = self.getBaseList(id)
                res["battle"]["zjcDPS"] = int(safe_divide(res["battle"]["zjcDPS"], self.detail["P1Time"]))
                res["battle"]["zflDPS1"] = int(safe_divide(res["battle"]["zflDPS1"], self.detail["P2Time1"]))
                res["battle"]["zflDPS2"] = int(safe_divide(res["battle"]["zflDPS2"], self.detail["P2Time2"]))
                res["battle"]["jfDPS1"] = int(safe_divide(res["battle"]["jfDPS1"], self.detail["P2Time1"]))
                res["battle"]["jfDPS2"] = int(safe_divide(res["battle"]["jfDPS2"], self.detail["P2Time2"]))
                bossResult.append(res)
        # bossResult.sort(key=lambda x: -x[2])
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
                        if self.bld.info.getName(event.target) in ["张景超", "張景超"]:
                            self.bh.setMainTarget(event.target)
                            self.statDict[event.caster]["battle"]["zjcDPS"] += event.damageEff
                        elif self.bld.info.getName(event.target) in ["张法雷", "張法雷"]:
                            if self.phase == 2:
                                self.statDict[event.caster]["battle"]["zflDPS1"] += event.damageEff
                            else:
                                self.statDict[event.caster]["battle"]["zflDPS2"] += event.damageEff
                        elif self.bld.info.getName(event.target) in ["劲风", "勁風"]:
                            if self.phase == 2:
                                self.statDict[event.caster]["battle"]["jfDPS1"] += event.damageEff
                            else:
                                self.statDict[event.caster]["battle"]["jfDPS2"] += event.damageEff

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

            if event.id == "23235":  # 疾雷·瞄准
                if event.stack == 1:
                    self.bh.setCall("23235", "疾雷·瞄准", "4224", event.time, 5000, event.target, "排枪点名")

            if event.id == "23274":  # 绝风疾
                if event.stack == 1:
                    self.bh.setCall("23274", "绝风疾", "4564", event.time, 7000, event.target, "消枪点名")

            if event.id == "23361":  # 万钧
                if event.stack == 1:
                    self.wanjunStart[event.target] = event.time
                    self.stunCounter[event.target].setState(event.time, 1)
                    self.stunCounter[event.target].setState(event.time + 20000, 0)
                else:
                    self.bh.setCall("23361", "万钧", "3426", self.wanjunStart[event.target], event.time - self.wanjunStart[event.target], event.target, "万钧点名定身")
                    if self.stunCounter[event.target].log[-1][0] > event.time:
                        del self.stunCounter[event.target].log[-1]
                    self.stunCounter[event.target].setState(event.time, 0)

        elif event.dataType == "Shout":
            if event.content in ['"到此为止了！"']:
                pass
            elif event.content in ['"四分五裂！"']:
                pass
            elif event.content in ['"迅如疾雷！"']:
                pass
            elif event.content in ['"呵！"']:
                pass
            elif event.content in ['"死吧！"']:
                pass
            elif event.content in ['"疾风枭首！"']:
                pass
            elif event.content in ['"无处可逃！"']:
                pass
            elif event.content in ['"哼，我才不会死在你们手里！"']:
                pass
            elif event.content in ['"有敌袭！"']:
                pass
            elif event.content in ['"狂风！席卷一切！"']:
                self.changePhase(event.time, 0)
                if self.firstPhase2:
                    self.setTimer("phase", event.time + 13000, 2)
                    self.firstPhase2 = 0
                else:
                    self.setTimer("phase", event.time + 13000, 3)
                self.bh.setBadPeriod(event.time, event.time + 13000, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                # 外场球打完了之后本来就没东西打，所以不管了，看mrdps吧
            elif event.content in ['"都滚开！"']:
                self.changePhase(event.time, 1)
                # self.setTimer("phase", event.time + 2000, 2)
                self.bh.setBadPeriod(event.time, event.time + 2000, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"又一次……走错路了吗……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"都死在这吧！"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["张景超宝箱", "張景超寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
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
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
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
        self.activeBoss = "张景超"

        self.initPhase(3, 1)
        self.firstPhase2 = 1

        self.bhBlackList.extend(["s31089", "s32392", "s31146", "b23271", "s31253", "s31259", "s31152", "b23274",
                                 "b23360", "n112005", "b23361", "c31935", "s31294", "s31327", "s32943", "n111977",
                                 "s31324", "s31297", "c31296", "n112915", "b23235", "s31267", "s31150",
                                 "c31293", "c31326", "n112022", "n112029", "c31803", "s31803", "s31296", "n112061",
                                 "s31325", "s31851", "n112875", "n112464", "n112491", "n112501", "n112461", "c31936",
                                 "n112524", "s33455"
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c31145": ["3452", "#773333", 2000],  # 迅风裂
                       "c31102": ["4224", "#ff7700", 5000],  # 疾雷
                       "c31152": ["3408", "#7700ff", 5000],  # 刀止横流
                       "c31148": ["4564", "#00ffff", 0],  # 绝风疾
                       "c31260": ["4222", "#ff7777", 5000],  # 万钧
                       "c31328": ["2146", "#ff77cc", 7000],  # 逆闪
                       "c31851": ["3434", "#ff77ff", 7000],  # 霆鸣
                       "c33130": ["2028", "#ff0000", 20000],  # 风雷灭尽
                       }

        # 张景超数据格式：
        # 7 ？

        self.wanjunStart = {}

        for line in self.bld.info.player:
            # self.stat[line].extend([0, 0, 0])
            self.statDict[line]["battle"] = {"zjcDPS": 0,
                                             "zflDPS1": 0,
                                             "jfDPS1": 0,
                                             "zflDPS2": 0,
                                             "jfDPS2": 0,
                                             }
            self.wanjunStart[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

