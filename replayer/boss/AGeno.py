# Created by moeheart at 04/07/2022
# 阿阁诺的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.BattleHistory import BattleHistory
from replayer.TableConstructorMeta import TableConstructorMeta
from replayer.utils import CriticalHealCounter, DpsShiftWindow
from tools.Functions import *

import tkinter as tk
        
class AGenoWindow(SpecificBossWindow):
    '''
    阿阁诺的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''

        self.constructWindow("阿阁诺", "1200x800")
        window = self.window

        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)
        
        self.constructCommonHeader(tb, "")
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

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class AGenoReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''
        self.countFinalOverall()
        self.bh.setEnvironmentInfo(self.bhInfo)

        for player in self.toushiPlayer:
            self.potList.append([self.bld.info.player[player].name,
                                 self.occDetailList[player],
                                 3,
                                 self.bossNamePrint,
                                 "指挥投石车",
                                 ["指挥投石车的补贴记录"]])

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
                            self.bh.setEnvironment(event.id, skillName, "13", event.time, 0, 1, "招式命中玩家", "skill")

            else:
                if event.caster in self.bld.info.player and event.caster in self.stat:
                    self.stat[event.caster][2] += event.damageEff
                if event.id == "30076":
                    self.toushiPlayer[event.caster] = 1

        elif event.dataType == "Buff":
            if event.target not in self.bld.info.player:
                return

            if event.id == "22741" and event.stack == 1:  # 蝠击锁定
                self.bh.setCall("22741", "蝠击锁定", "4576", event.time, 0, event.target, "点名圈")

            if event.caster in self.bld.info.npc and event.stack > 0:
                # 尝试记录buff事件
                name = "b%s" % event.id
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 10000:
                    self.bhTime[name] = event.time
                    skillName = self.bld.info.getSkillName(event.full_id)
                    if "," not in skillName:
                        self.bh.setEnvironment(event.id, skillName, "13", event.time, 0, 1, "玩家获得气劲", "buff")

            if event.id == "22589":
                if event.stack < 20:
                    self.shitouCount[event.stack] += 1
                    if self.shitouCount[event.stack] == 8:  # 平滑阈值
                        self.shitouLast = self.shitouStack
                        self.shitouStack = event.stack
                        for i in range(20):
                            if i != self.shitouStack:
                                self.shitouCount[i] = 0
                        if self.shitouStack > self.shitouLast and event.time - self.shitouLastTime > 10000:
                            self.bh.setEnvironment("0", "船出现", "3404", event.time, 0, 1, "NPC出现", "npc", "#333333")
                            self.shitouLastTime = event.time

        elif event.dataType == "Shout":
            if event.content in ['"喔？敢扰乱大人计划的，都得死！"']:
                pass
            elif event.content in ['"不好，火船就要靠近浮桥了！得赶紧推动机关！"']:
                pass
            elif event.content in ['"喝！都给我下去喂鱼吧！"']:
                self.bh.setBadPeriod(event.time - 5000, event.time + 5000, True, True)
            elif event.content in ['"妈的！你们给我等着！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            else:
                # self.bh.setEnvironment("0", event.content, "13", event.time, 0, 1, "喊话", "shout")
                pass
            return

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name in ["n108111", "n108109", "n108110"]:
                    name = "n01"
                    skillName = "船出现"
                # if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                #     self.bhTime[name] = event.time
                #     if "的" not in skillName:
                #         self.bh.setEnvironment(self.bld.info.npc[event.id].templateID, skillName, "13", event.time, 0,
                #                                1, "NPC出现", "npc")
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name in ["阿阁诺宝箱", "阿閣諾寶箱"]:
                self.win = 1

        elif event.dataType == "Death":  # 重伤记录
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["阿阁诺", "阿閣諾"]:
                self.win = 1

        elif event.dataType == "Battle":  # 战斗状态变化
            if self.bld.info.getName(event.id) in ["阿阁诺"]:
                self.firstBattle = 0
                if event.time - self.startTime > 500 and self.firstBattle:  # 预留500ms的空白时间
                    self.bh.setBadPeriod(self.startTime, event.time - 500, True, True)

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
        self.activeBoss = "阿阁诺"

        self.toushiPlayer = {}  # 投石

        self.bhBlackList.extend(["s28", "s30069", "b22589", "s30405", "s30070", "s30071",
                                 "b22620", "s30068", "c30086"])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"b22741": ["4576", "#ff00ff"],  # 蝠击锁定
                       "c30071": ["3436", "#ff7700"],  # 黑血风遁
                       "s30086": ["342", "#00ff00"],  # 磐翼裹身
                       }

        self.shitouStack = 0
        self.shitouLast = 0
        self.shitouLastTime = 0
        self.shitouCount = [0] * 20  # BOSS的石头统计有时会因为重伤乱掉，所以加一个平滑

        for line in self.bld.info.player:
            pass

        self.firstBattle = 1

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

