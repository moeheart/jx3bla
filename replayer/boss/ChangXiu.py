# Created by moeheart at 04/07/2022
# 常宿的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class ChangXiuWindow(SpecificBossWindow):
    '''
    常宿的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("常宿", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "伐逆点名只计3秒，伐乱点名只计4秒，奉天伐恶会全程记录。")
        tb.AppendHeader("P1DPS", "在P1阶段，也即70%%以上的输出。\nP1时间：%s，这个时间不包括第一次内场。" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "在P2阶段，也即70%%以下的输出。\nP2时间：%s，这个时间包括第二次内场。" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("黑字次数", "踩到黑字的次数。\n虽然不会死，但是作者就是这么无聊。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)
            tb.AppendContext(int(line[7]))
            tb.AppendContext(int(line[8]))
            tb.AppendContext(int(line[9]))
            # 心法复盘
            if line[0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line[0]], line[0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class ChangXiuReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        if self.phase != 0 and self.phaseTime[self.phase] == 0:
            self.phaseTime[self.phase] = self.finalTime - self.phaseStart

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)

        self.bh.setEnvironmentInfo(self.bhInfo)

        # for line in self.bh.log["environment"]:
        #     timePrint = "%.1f" % ((line["start"] - self.startTime) / 1000)
        #     print(timePrint, line["type"], line["skillname"], line["skillid"])

    def getResult(self):
        '''
        生成复盘结果的流程。需要维护effectiveDPSList, potList与detail。
        '''

        self.countFinal()

        bossResult = []
        for id in self.bld.info.player:
            if id in self.stat:
                line = self.stat[id]
                if id in self.equipmentDict:
                    line[4] = self.equipmentDict[id]["score"]
                    line[5] = "%s|%s" % (self.equipmentDict[id]["sketch"], self.equipmentDict[id]["forge"])
                else:
                    line[5] = "|"

                line[6] = self.stunCounter[id].buffTimeIntegral() / 1000

                if getOccType(self.occDetailList[id]) == "healer":
                    line[3] = int(self.hps[id] / self.battleTime * 1000)

                dps = int(line[2] / self.battleTime * 1000)
                bossResult.append([line[0],
                                   line[1],
                                   dps,
                                   line[3],
                                   line[4],
                                   line[5],
                                   line[6],
                                   int(line[7] / (self.detail["P1Time"] + 1e-10)),
                                   int(line[8] / (self.detail["P2Time"] + 1e-10)),
                                   line[9],
                                   ])
        bossResult.sort(key=lambda x: -x[2])
        self.effectiveDPSList = bossResult

        return self.effectiveDPSList, self.potList, self.detail

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

                if event.id == "30436":
                    self.stat[event.target][9] += 1

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff

                    if event.target in self.bld.info.npc:
                        if self.phase == 1:
                            self.stat[event.caster][7] += event.damageEff
                        elif self.phase == 2:
                            self.stat[event.caster][8] += event.damageEff
                            if self.phaseStart == 0:
                                self.phaseStart = event.time

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "22494" and event.stack == 1:  # 罪印
                self.bh.setCall("22494", "罪印", "3431", event.time, 0, event.target, "罪印点名")
            if event.id == "22493" and event.stack == 1:  # 罚印
                self.bh.setCall("22493", "罚印", "3430", event.time, 0, event.target, "罚印点名")

            if event.id == "22229":  # 伐乱
                if event.stack == 1:
                    self.bh.setCall("22229", "伐乱", "3409", event.time, 0, event.target, "伐乱点名，排圈")
                    self.stunCounter[event.target].setState(event.time, event.stack)
                    self.stunCounter[event.target].setState(event.time + 4000, 0)

            if event.id == "22246":  # 伐逆
                if event.stack == 1:
                    self.bh.setCall("22246", "伐逆", "2141", event.time, 0, event.target, "伐逆点名，排矩形")
                    self.stunCounter[event.target].setState(event.time, event.stack)
                    self.stunCounter[event.target].setState(event.time + 3000, 0)

            if event.id == "22331":  # 奉天伐恶
                if event.stack == 1:
                    self.bh.setCall("22331", "奉天伐恶", "12451", event.time, 0, event.target, "奉天伐恶点名，沉默")
                self.stunCounter[event.target].setState(event.time, event.stack)

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

        elif event.dataType == "Shout":
            if event.content in ['"来吧！"']:
                pass
            elif event.content in ['"喝啊！"']:
                pass
            elif event.content in ['"罪！"']:
                pass
            elif event.content in ['"罚！"']:
                pass
            elif event.content in ['"乱！"']:
                pass
            elif event.content in ['"罪！罚！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                if self.phase == 1:
                    self.phaseTime[1] = event.time - self.phaseStart
                self.phase = 2
                self.phaseStart = event.time
            elif event.content in ['"哼！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                self.win = 1
            elif event.content in ['"你我……再会……"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                self.win = 1
            else:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")
            return

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                # if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                #     self.bhTime[name] = event.time
                #     if "的" not in skillName:
                #         self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                #                                1, "NPC出现", "npc")

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

            if event.id == "30456" and self.phase == 1:  # 墨言可畏
                self.phaseTime[1] = event.time - self.phaseStart
                self.phase = 2
                self.phaseStart = 0

                    
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
        self.activeBoss = "通用"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 常宿数据格式：
        # 7 P1DPS, 8 P2DPS, 9 黑字次数
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.stunCounter = {}
        self.phase = 1
        self.phaseStart = self.startTime
        self.phaseTime = [0, 0, 0]

        self.bhTime = {}
        self.bhBlackList.extend(["n108727", "n108738",
                                 "s30044", "s30055", "b22228", "b22660", "b22197", "n108264", "s30048", "c30051", "s30056",
                                 "n108121", "n108257", "b22192", "s30158", "s30157", "c30157", "c30158", "b22199", "b22229",
                                 "s30134", "b22190", "b22494", "n108629", "b22493", "b22195", "b22191", "s30060",
                                 "c30216", "s30216", "b22622",
                                 "c30436", "s30436", "c30437", "s30437",
                                 "c30188", "s30188", "s30191", "c30190", "s30190", "s30192", "c30217", "s30217", "b22340",
                                 "b22335", "b22342",
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"s30047": ["2019", "#ff00ff"],  # 罪笞
                       "b22246": ["2141", "#7777ff"],  # 伐逆buff
                       "c30140": ["2024", "#0000ff"],  # 伐逆读条(lvl1/2)
                       "c30888": ["3431", "#0077ff"],  # 罪印
                       "c30048": ["2021", "#00ffff"],  # 罪挥
                       "c30159": ["3409", "#ff0077"],  # 伐乱·罪影
                       "c30889": ["3430", "#ff77cc"],  # 罚印
                       "s30085": ["3436", "#ff0000"],  # 罪笞·鞭挞
                       "c30056": ["4531", "#ff7700"],  # 罚绞
                       "c30059": ["2028", "#00ff00"],  # 伐违
                       "c30060": ["2028", "#77ff77"],  # 伐违·御
                       "c30456": ["3399", "#007777"],  # 墨言可畏
                       "b22331": ["12451", "#ff0077"],  # 奉天伐恶
                       }

        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0]
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

