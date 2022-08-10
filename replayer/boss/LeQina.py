# Created by moeheart at 04/07/2022
# 勒齐纳的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class LeQinaWindow(SpecificBossWindow):
    '''
    勒齐纳的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.constructWindow("勒齐那", "1200x900")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)
        
        self.constructCommonHeader(tb, "包括被[翻找口袋]点名火、油圈的时间，以及搬炸弹的时间。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()
        
        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            # 心法复盘
            if line[0] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line[0]], line[0])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        frame2 = tk.Frame(window)
        frame2.pack()
        tb = TableConstructorMeta(self.config, frame2)
        tb.AppendHeader("炸弹复盘", "")
        tb.EndOfLine()
        for line in self.detail["zhadan"]:
            name = self.getMaskName(line[1])
            occ = line[2]
            color = getColor(occ)
            tb.AppendContext(name, color=color)
            tb.AppendContext("拿起炸弹")
            tb.AppendContext(line[3])
            tb.AppendContext("放下炸弹")
            tb.AppendContext(line[4])
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class LeQinaReplayer(SpecificReplayerPro):

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
                res = self.getBaseList(id)
                bossResult.append(res)
        bossResult.sort(key=lambda x:-x[2])
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
                            self.bh.setEnvironment(event.id, skillName, "13", event.time, 0, 1, "招式命中玩家", "skill")
                    
            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                
        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "22614":  # 翻找口袋·燃火
                if event.stack == 1:
                    self.bh.setCall("22614", "翻找口袋·燃火", "12376", event.time, 0, event.target, "点名排火圈")
                self.stunCounter[event.target].setState(event.time, event.stack)
            if event.id == "22615":  # 翻找口袋·污油
                if event.stack == 1:
                    self.bh.setCall("22615", "翻找口袋·污油", "2025", event.time, 0, event.target, "点名排油圈")
                self.stunCounter[event.target].setState(event.time, event.stack)
            if event.id == "22487" and event.stack == 1:  # 火刑
                self.bh.setCall("22487", "火刑", "14833", event.time, 0, event.target, "火刑锁足")
            if event.id == "22477" and event.stack == 1:  # 焚骨
                self.bh.setCall("22477", "焚骨", "12452", event.time, 0, event.target, "焚骨点名")
            if event.id == "22411":  # 搬运炸弹
                if event.stack == 1:
                    self.bh.setCall("22411", "轻拿轻放", "10473", event.time, 0, event.target, "搬运炸弹")
                    self.detail["zhadan"].append([event.target, self.bld.info.player[event.target].name,
                                                  self.bld.info.player[event.target].occ,
                                                  parseTime((event.time - self.startTime)/1000),
                                                  "未知"])
                else:
                    for i in range(len(self.detail["zhadan"])):
                        if self.detail["zhadan"][i][0] == event.target and self.detail["zhadan"][i][4] == "未知":
                            self.detail["zhadan"][i][4] = parseTime((event.time - self.startTime)/1000)
                self.stunCounter[event.target].setState(event.time, event.stack)

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "13", event.time, 0, 1, "玩家获得气劲", "buff")
                    
        elif event.dataType == "Shout":
            if event.content in ['"皆成灰烬！"']:
                pass
            elif event.content in ['"无处可逃！"']:
                pass
            elif event.content in ['"燃起来吧！"']:
                pass
            elif event.content in ['"幸而即时，都已经灭了。不过……河阳戒备森严，此人却能轻易闯入……"']:
                pass
            elif event.content in ['"火，怎么熄灭了……"']:
                self.win = 1
            else:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout")


        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
            #     name = "n%s" % self.bld.info.npc[event.id].templateID
            #     if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
            #         self.bhTime[name] = event.time
            #         skillName = self.bld.info.npc[event.id].name
            #         if "的" not in skillName:
            #             self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "340", event.time, 0, 1, "NPC出现", "npc")
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name in ["勒齐那宝箱", "勒齊那寶箱"]:
                self.win = 1
                
        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["勒齐那"]:
                self.win = 1
            
        elif event.dataType == "Battle":  # 战斗状态变化
            pass

        elif event.dataType == "Cast":  # 施放技能事件，jcl专属
            if event.caster in self.bld.info.npc:  # 记录非玩家施放的技能
                name = "c%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "13", event.time, 0, 1, "招式开始运功", "cast")

                    
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
        self.activeBoss = "勒齐那"

        self.detail["zhadan"] = []  # 搬炸弹复盘

        self.bhBlackList.extend(["s30500", "s30461", "s30275", "c3365", "b22615", "b22614", "s6746", "b17933", "b6131",
                                 "s30335", "s30334", "b22400", "s30462", "s30333", "b22402", "b22401",
                                 "b22478", "s30370", "s30368", "s30369"])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"s30274": ["12375", "#ff7700"],  # 燃焰横扫
                       "c30838": ["14155", "#7777ff"],  # 污油喷溅
                       "c30278": ["12376", "#ff00ff"],  # 翻找口袋
                       "b22487": ["14833", "#ff0000"],  # 火刑
                       "b22477": ["12452", "#ff0077"],  # 焚骨
                       }
        
        for line in self.bld.info.player:
            pass

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

