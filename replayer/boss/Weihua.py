# Created by moeheart at 09/16/2023
# 魏华的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class WeiHuaWindow(SpecificBossWindow):
    '''
    翁幼之的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("魏华", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("纳元次数", "被秋阳神功·纳元命中的次数。\n需要注意的是，每个矩形只会随机选择5个目标，所以即使站位正确，也不一定会被统计在次数中。")
        tb.AppendHeader("破野次数", "被秋阳神功·破野命中的次数。\n需要注意的是，每个内力球只有前5次命中有效，所以即使被统计在次数中，也不一定说明站位正确。")
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["numNayuan"]))
            tb.AppendContext(int(line["battle"]["numPoye"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class WeiHuaReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

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
                            key = "s%s" % event.id
                            if key in self.bhInfo or self.debug:
                                self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "招式命中玩家", "skill")

                if event.id == "35461":
                    # 纳元
                    self.statDict[event.target]["battle"]["numNayuan"] += 1

                if event.id == "35606":
                    # 破野
                    self.statDict[event.target]["battle"]["numPoye"] += 1

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["魏华", "魏華"]:
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
                        key = "b%s" % event.id
                        if key in self.bhInfo or self.debug:
                            self.bh.setEnvironment(event.id, skillName, "341", event.time, 0, 1, "玩家获得气劲", "buff")

        elif event.dataType == "Shout":
            if event.content in ['"谁？！别过来！别逼我出手！"', '"誰？！ 別過來！ 別逼我出手！"']:
                pass
            elif event.content in ['"……"', '"啊啊啊啊啊啊啊！好痛！"', '""']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"看招！"']:
                pass
            elif event.content in ['"再接我这招！"']:
                pass
            elif event.content in ['"哈啊！！！"']:
                pass
            elif event.content in ['"秋阳……神功！"']:
                pass
            elif event.content in ['"啊……怎么会……"']:
                pass
            elif event.content in ['"华儿贪恋江湖浮名，终究还是被这邪功反噬了……侠士，请先退下，我要将这秋阳神功压住！"']:
                pass
            elif event.content in ['"秋阳暴而草木殒……希望我来得还不算晚。"']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            # if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["翁幼之宝箱", "??寶箱"]:
            #     self.win = 1
            #     self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            if event.id in self.bld.info.npc and event.enter and self.bld.info.npc[event.id].name != "":
                name = "n%s" % self.bld.info.npc[event.id].templateID
                skillName = self.bld.info.npc[event.id].name
                if name not in self.bhBlackList and event.time - self.bhTime.get(name, 0) > 3000:
                    self.bhTime[name] = event.time
                    if "的" not in skillName:
                        key = "n%s" % self.bld.info.npc[event.id].templateID
                        if key in self.bhInfo or self.debug:
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
            # if self.bld.info.getSkillName(event.full_id) in ["血影坠击", "怨·黄泉鬼步"]:
            #     print("[Xueyingzhuiji]", event.id, parseTime((event.time - self.startTime) / 1000))

                    
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
        self.activeBoss = "魏华"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["b25691", "n123664", "s35454", "b26592", "b26591", "b26678", "s35452",
                                 "n124597", "n124871", "n125462", "n122406", "n125101", "b26683", "n125224",
                                 "b26684", "s35607", "s35461", "n125518", "s35606", "b26632", "b26676", "n125865",
                                 "n125721", "n125716", "n125519", "n125115", "n125523", "n125512",
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       "c35452": ["4549", "#ff00ff", 3000],  # 泉映千山·清流
                       "s35453": ["4516", "#ff0000", 0],  # 泉映千山·苍羽
                       "s35419": ["345", "#0000ff", 0],  # 泉映千山·暮白
                       # b26591暮白
                       "c35636": ["4498", "#ff0077", 1000],   # 泉映千山·游龙荡影
                       # b26678点名游龙荡影
                       "c35457": ["3428", "#003300", 5000],  # 秋阳神功·起式
                       "c35460": ["2023", "#77ff00", 5000],  # 秋阳神功·纳元
                       # b26683纳元
                       "c35462": ["2024", "#77ff77", 5000],  # 秋阳神功·破野
                       # b26684破野
                       "c35465": ["3429", "#007700", 3000],  # 秋阳神功·终式
                       }

        # 魏华数据格式：
        # 7 ？

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"numNayuan": 0,
                                             "numPoye": 0}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

