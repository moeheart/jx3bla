# Created by moeheart at 04/07/2022
# 周贽的定制复盘库。
# 功能待定。

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class ZhouZhiWindow(SpecificBossWindow):
    '''
    周贽的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.setTimelineWindow(self.bh, "周贽")

        window = tk.Toplevel()
        window.title('周贽复盘')
        window.geometry('1200x900')
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)
        
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效DPS", "全程DPS。与游戏中不同的是，重伤时间也会被计算在内。")
        tb.AppendHeader("团队-心法DPS", "综合考虑当前团队情况与对应心法的全局表现，计算的百分比。平均水平为100%。")
        tb.AppendHeader("装分", "玩家的装分，可能会获取失败。")
        tb.AppendHeader("详情", "装备详细描述，暂未完全实装。")
        tb.AppendHeader("强化", "装备强化列表，表示[精炼满级装备数量]/[插8]-[插7]-[插6]/[五彩石等级]/[紫色附魔]-[蓝色附魔]/[大附魔：手腰脚头衣裤]")
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。\n包括被瞄准点名的时间。")
        tb.AppendHeader("P1DPS", "对狼牙精锐的输出。\nP1时间：%s" % parseTime(self.detail["P1Time"]))
        tb.AppendHeader("P2DPS", "对李秦授的输出。\nP2时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("骑兵DPS", "对狼牙骑兵的输出，通常用于转火的参考。\n分母以P1和P2的时间相加计算。")
        tb.AppendHeader("P3DPS", "对周贽本体的输出。\nP3时间：%s" % parseTime(self.detail["P3Time"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            name = self.getMaskName(self.effectiveDPSList[i][0])
            color = getColor(self.effectiveDPSList[i][1])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(int(self.effectiveDPSList[i][2]))

            if getOccType(self.effectiveDPSList[i][1]) != "healer":
                text3 = str(self.effectiveDPSList[i][3]) + '%'
                color3 = "#000000"
            else:
                text3 = self.effectiveDPSList[i][3]
                color3 = "#00ff00"
            tb.AppendContext(text3, color=color3)
            
            text4 = "-"
            if self.effectiveDPSList[i][4] != -1:
                text4 = int(self.effectiveDPSList[i][4])
            color4 = "#000000"
            if "大橙武" in self.effectiveDPSList[i][5]:
                color4 = "#ffcc00"
            tb.AppendContext(text4, color=color4)
            
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[0])
            tb.AppendContext(self.effectiveDPSList[i][5].split('|')[1])
            tb.AppendContext(int(self.effectiveDPSList[i][6]))

            tb.AppendContext(int(self.effectiveDPSList[i][7]))
            tb.AppendContext(int(self.effectiveDPSList[i][8]))
            tb.AppendContext(int(self.effectiveDPSList[i][9]))
            tb.AppendContext(int(self.effectiveDPSList[i][10]))

            # 心法复盘
            if self.effectiveDPSList[i][0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[self.effectiveDPSList[i][0]], self.effectiveDPSList[i][0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("军阵复盘", "")
        tb.EndOfLine()
        for line in self.detail["junzhen"]:
            for record in line["log"]:
                name = self.getMaskName(record[1])
                occ = record[2]
                color = getColor(occ)
                tb.AppendContext(name, color=color)
                tb.AppendContext("%s%s" % (record[3], record[4]))
            tb.EndOfLine()

        frame3 = tk.Frame(window)
        frame3.pack()
        buttonPrev = tk.Button(frame3, text='<<', width=2, height=1, command=self.openPrev)
        submitButton = tk.Button(frame3, text='战斗事件记录', command=self.openPot)
        timelineButton = tk.Button(frame3, text='时间轴', command=self.openTimelineWindow)
        buttonNext = tk.Button(frame3, text='>>', width=2, height=1, command=self.openNext)
        buttonPrev.grid(row=0, column=0)
        submitButton.grid(row=0, column=1)
        timelineButton.grid(row=0, column=2)
        buttonNext.grid(row=0, column=3)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, config, effectiveDPSList, detail, occResult, bh):
        super().__init__(config, effectiveDPSList, detail, occResult)
        self.bh = bh

class ZhouZhiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        if self.phase != 0 and self.phaseTime[self.phase] == 0:
            self.phaseTime[self.phase] = self.finalTime - self.phaseStart

        self.detail["P1Time"] = int(self.phaseTime[1] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[2] / 1000)
        self.detail["P3Time"] = int(self.phaseTime[3] / 1000)

        self.bh.setEnvironmentInfo(self.bhInfo)

        for player in self.junzhenPlayer:
            name = ["", "刀兵", "弓兵", "戟兵"][self.junzhenPlayer[player]]
            self.potList.append([self.bld.info.player[player].name,
                                 self.occDetailList[player],
                                 3,
                                 self.bossNamePrint,
                                 "军阵：%s" % name,
                                 ["指挥军阵的补贴记录"]])

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

                line[6] = int(self.stunCounter[id].buffTimeIntegral() / 1000)

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
                                   int(line[9] / (self.detail["P1Time"] + self.detail["P2Time"] + 1e-10)),
                                   int(line[10] / (self.detail["P3Time"] + 1e-10)),
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

                if event.id == "30160":  # 刀兵换位
                    self.junzhenPlayer[event.caster] = 1
                    if self.detail["junzhen"] != []:
                        self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                             self.bld.info.player[event.caster].occ,
                                                             parseTime((event.time - self.startTime) / 1000),
                                                             "换位"])
                elif event.id == "30161":  # 弓兵换位
                    self.junzhenPlayer[event.caster] = 2
                    if self.detail["junzhen"] != []:
                        self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                             self.bld.info.player[event.caster].occ,
                                                             parseTime((event.time - self.startTime) / 1000),
                                                             "换位"])
                elif event.id == "30162":  # 戟兵换位
                    self.junzhenPlayer[event.caster] = 3
                    if self.detail["junzhen"] != []:
                        self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                             self.bld.info.player[event.caster].occ,
                                                             parseTime((event.time - self.startTime) / 1000),
                                                             "换位"])
                elif event.id == "30163":  # 刀兵技能
                    self.detail["junzhen"].append({"log": []})
                    self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                         self.bld.info.player[event.caster].occ,
                                                         parseTime((event.time - self.startTime) / 1000),
                                                         "立盾"])
                elif event.id == "30164":  # 弓兵技能
                    if self.detail["junzhen"] == []:
                        self.detail["junzhen"].append({"log": []})
                    if self.detail["junzhen"][-1]["log"] != [] and self.detail["junzhen"][-1]["log"][-1][4][:2] == "射箭":
                        num = 1
                        if len(self.detail["junzhen"][-1]["log"][-1][4]) > 2:
                            num = int(self.detail["junzhen"][-1]["log"][-1][4][3:])
                        num += 1
                        self.detail["junzhen"][-1]["log"][-1][4] = "射箭*%d" % num
                    else:
                        self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                         self.bld.info.player[event.caster].occ,
                                                         parseTime((event.time - self.startTime) / 1000),
                                                         "射箭"])
                elif event.id == "30165":  # 戟兵技能
                    if self.detail["junzhen"] == []:
                        self.detail["junzhen"].append({"log": []})
                    self.detail["junzhen"][-1]["log"].append([event.caster, self.bld.info.player[event.caster].name,
                                                         self.bld.info.player[event.caster].occ,
                                                         parseTime((event.time - self.startTime) / 1000),
                                                         "列阵"])

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff

                    if event.target in self.bld.info.npc:
                        if self.bld.info.npc[event.target].name in ["狼牙精锐"]:
                            self.stat[event.caster][7] += event.damageEff
                            if self.phase == 0:
                                self.phase = 1
                                self.phaseStart = event.time
                        elif self.bld.info.npc[event.target].name in ["李秦授"]:
                            self.stat[event.caster][8] += event.damageEff
                            if self.phase == 1:
                                self.phase = 2
                                self.phaseStart = event.time
                        elif self.bld.info.npc[event.target].name in ["狼牙铁骑"]:
                            self.stat[event.caster][9] += event.damageEff
                        elif self.bld.info.npc[event.target].name in ["周贽"]:
                            self.stat[event.caster][10] += event.damageEff
                            if self.phase == 2:
                                self.phase = 3
                                self.phaseStart = event.time

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "22440" and event.stack == 1:  # 瞄准
                self.bh.setCall("22440", "瞄准", "3293", event.time, 0, event.target, "精准射击的目标")

            if event.id == "22440":  # 瞄准
                if event.stack == 1:
                    self.bh.setCall("22440", "瞄准", "3293", event.time, 0, event.target, "精准射击的目标")
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
            if event.content in ['"先锋出击！"']:
                pass
            elif event.content in ['"列阵！迎敌！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "Shout", "#333333")
            elif event.content in ['"杀！"']:
                pass
            elif event.content in ['"杀啊！"']:
                pass
            elif event.content in ['"放箭！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"立盾！"']:
                pass
            elif event.content in ['"呃……"']:
                pass
            elif event.content in ['"“赤枪鬼”在此！今日定要杀你们个片甲不留！！"', '"“赤枪鬼”在此！今日定要杀你们个片甲不留！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                if self.phase == 1:
                    self.phaseTime[1] = event.time - self.phaseStart
            elif event.content in ['"已降服敌将！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                if self.phase == 2:
                    self.phaseTime[2] = event.time - self.phaseStart
            elif event.content in ['"好！敌将被俘，士气大减。"']:
                pass
            elif event.content in ['"骑兵听令，出城助战！"']:
                pass
            elif event.content in ['"骑兵先头冲阵，尔等紧随其后，杀！"']:
                pass
            elif event.content in ['"哼！就凭你们这点人马，还妄想打败我狼牙大军？"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"报！狼牙断旗在此，我军生擒敌将徐璜玉，北门告捷！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                self.win = 1
                self.phaseTime[3] = event.time - self.phaseStart
            elif event.content in ['"撤！"']:
                pass
            elif event.content in ['"乘胜追击！"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")
            return

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    # if "的" not in skillName:
                    #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                    #                            1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            pass

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            if event.content in ['"黄河水位即将上涨！"']:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "系统警告", "Alert")

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
        self.activeBoss = "通用"
        
        # 通用格式：
        # 0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间

        # 周贽数据格式：
        # 7 P1DPS, 8 P2DPS, 9 骑兵DPS, 10 P3DPS
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.junzhenPlayer = {}  # 军阵
        self.junzhenNum = 0
        self.stunCounter = {}
        self.phase = 0
        self.phaseStart = self.startTime
        self.phaseTime = [0, 0, 0, 0]

        self.detail["junzhen"] = []  # 军阵复盘


        self.bhTime = {}
        self.bhBlackList.extend(["n108172", "b22316", "b22315", "s30459", "c30139", "b22227", "b22317", "s30178",
                                 "n108174", "n108127", "n108126", "n108125", "n108515", "s30046", "s30210", "s30329", "b22449",
                                 "n108223", "n108224", "n108225", "s30139", "s30440", "s30341", "s30340",
                                 "n108676", "n108682", "n108642", "n108639", "n109125", "n109129", "n109126", "n109127", "n109128",
                                 "n109096", "n108269", "n108687", "n108685", "s30319", "n108265", "n108266", "n108268",
                                 "n108260", "n108267", "n108638", "b22318", "c30083", "s30318", "b22440", "s30408", "s30330",
                                 "s30332", "s30409", "b22472", "s30270", "s30460", "s30272", "s30320", "c30132", "c30433",
                                 "b22447"
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"s30179": ["11343", "#00ffff"],  # 箭雨
                       "c30327": ["3293", "#ff00ff"],  # 精准射击
                       "c30271": ["4576", "#ff7700"],  # 横扫
                       "c30323": ["3450", "#7700ff"],  # 贯体箭
                       "c30270": ["342", "#7777ff"],  # 挥击P1
                       "c30460": ["342", "#7777ff"],  # 挥击P2
                       "c30272": ["3436", "#0000ff"],  # 突刺
                       "c30330": ["2028", "#ff0000"],  # 摧山
                       "c30332": ["4504", "#773333"],  # 震岳
                       "b22448": ["4544", "#00ff00"],  # 冲锋目标
                       }

        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                [0, 0, 0, 0]
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

