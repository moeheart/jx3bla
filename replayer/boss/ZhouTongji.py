# Created by moeheart at 04/07/2022
# 周通忌的定制复盘库。
# 功能待定。

from replayer.boss.Base import SpecificReplayerPro, SpecificBossWindow, ToolTip
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class ZhouTongjiWindow(SpecificBossWindow):
    '''
    周通忌的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.setTimelineWindow(self.bh, "周通忌")
        self.setCombatTrackerWindow(self.act)

        window = tk.Toplevel()
        window.title('周通忌复盘')
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
        tb.AppendHeader("被控", "受到影响无法正常输出的时间，以秒计。\n包括被一箭一个点名的时间。")
        tb.AppendHeader("本体DPS", "对BOSS本体的DPS。")
        tb.AppendHeader("小怪DPS", "对小怪的DPS。")
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

            # 心法复盘
            if self.effectiveDPSList[i][0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[self.effectiveDPSList[i][0]], self.effectiveDPSList[i][0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("投石复盘", "")
        tb.EndOfLine()
        for line in self.detail["toushi"]:
            tb.AppendContext("%s喊话" % line["start"])
            for record in line["log"]:
                name = self.getMaskName(record[1])
                occ = record[2]
                color = getColor(occ)
                tb.AppendContext(name, color=color)
                tb.AppendContext("%s投石" % record[3])
            tb.EndOfLine()

        frame3 = tk.Frame(window)
        frame3.pack()
        buttonPrev = tk.Button(frame3, text='<<', width=2, height=1, command=self.openPrev)
        submitButton = tk.Button(frame3, text='战斗事件记录', command=self.openPot)
        actButton = tk.Button(frame3, text='数值统计', command=self.openCombatTrackerWindow, bg='#777777')
        timelineButton = tk.Button(frame3, text='时间轴', command=self.openTimelineWindow)
        buttonNext = tk.Button(frame3, text='>>', width=2, height=1, command=self.openNext)
        buttonPrev.grid(row=0, column=0)
        submitButton.grid(row=0, column=1)
        actButton.grid(row=0, column=2)
        timelineButton.grid(row=0, column=3)
        buttonNext.grid(row=0, column=4)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult)
        self.analysedBattleData = analysedBattleData
        self.bh = self.analysedBattleData["bossBh"]
        self.act = self.analysedBattleData["act"]

class ZhouTongjiReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

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
                                   int(line[7] / self.battleTime * 1000),
                                   int(line[8] / self.battleTime * 1000),
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

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.npc[event.target].name in ["周通忌"]:
                            self.stat[event.caster][7] += event.damageEff
                        elif self.bld.info.npc[event.target].name in ["狼牙精锐士兵"]:
                            self.stat[event.caster][8] += event.damageEff

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "22338":  # 一箭一个
                if event.stack == 1:
                    self.bh.setCall("22338", "一箭一个", "2911", event.time, 0, event.target, "一箭一个点名")
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
            if event.content in ['"撕碎你们！"']:
                pass
            elif event.content in ['"这！就是！"']:
                pass
            elif event.content in ['"狼牙！"']:
                pass
            elif event.content in ['"给我上！"']:
                pass
            elif event.content in ['"瞄准他们！"']:
                pass
            elif event.content in ['"……"']:
                pass
            elif event.content in ['"呀啊！！！！！！！！！"']:
                pass
            elif event.content in ['"让我看看你们的能耐！"', '"不痛不痒！哈哈哈哈哈！"', '"用点力！哼哈哈哈哈哈！"']:
                self.detail["toushi"].append({"start": parseTime((event.time - self.startTime) / 1000), "log": []})
            elif event.content in ['"今日就让你们见识见识，本将这副巨象铠甲的厉害！"']:
                pass
            elif event.content in ['"呕！"']:
                pass
            elif event.content in ['"啊……！糟……了……"']:
                self.win = 1
            elif event.content in ['"狼牙守将已亡，众将士！随我杀！"']:
                self.win = 1
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")
            return

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if skillName in ["狼牙精锐士兵", ""]:
                        self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, "小怪", "340", event.time, 0,
                                               1, "小怪出现", "npc", "#333333")

                    # if "的" not in skillName:
                    #     self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "341", event.time, 0,
                    #                            1, "NPC出现", "npc")

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["周通忌"]:
                self.win = 1

        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Alert":  # 系统警告框
            if event.content in ['"黄河水位即将上涨！"']:
                self.bh.setEnvironment("0", "涨潮", "2033", event.time, 0, 1, "系统警告", "alert", "#0077ff")
            elif event.content[-12:] in ['已呼叫投石车进行投掷。"']:
                name = event.content[1:-12]
                for id in self.bld.info.player:
                    if self.bld.info.player[id].name == name:
                        self.detail["toushi"][-1]["log"].append([id, self.bld.info.player[id].name,
                                                             self.bld.info.player[id].occ,
                                                             parseTime((event.time - self.startTime) / 1000)])

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

        # 周通忌数据格式：
        # 7 本体DPS 8 小怪DPS
        
        self.stat = {}
        self.hps = {}
        self.detail["boss"] = self.bossNamePrint
        self.win = 0
        self.bh = BattleHistory(self.startTime, self.finalTime)
        self.hasBh = True
        self.stunCounter = {}

        self.detail["toushi"] = []  # 投石复盘

        self.bhTime = {}
        self.bhBlackList.extend(["s28", "s30117", "s30449", "s30108", "b22275", "s30120", "s30121", "b22274",
                                 "s30115", "s30896", "b22338", "b22337", "s30118", ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"s30116": ["2021", "#ff0000"],  # 撕裂回旋
                       "c30106": ["2019", "#ff7700"],  # 这！就是！狼牙！
                       "c30172": ["2024", "#7700ff"],  # 象鼻横扫
                       "c30113": ["3426", "#ff00ff"],  # 象牙冲锋
                       "c30498": ["2911", "#0000ff"],  # 一箭一个
                       }

        for line in self.bld.info.player:
            self.hps[line] = 0
            self.stat[line] = [self.bld.info.player[line].name, self.occDetailList[line], 0, 0, -1, "", 0] + \
                              [0, 0]
            self.stunCounter[line] = BuffCounter(0, self.startTime, self.finalTime)

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

