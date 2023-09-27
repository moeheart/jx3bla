# Created by moeheart at 09/16/2023
# 麒麟的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class QilinWindow(SpecificBossWindow):
    '''
    麒麟的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("麒麟", "1200x800")
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

class QilinReplayer(SpecificReplayerPro):

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

            else:
                if event.caster in self.bld.info.player and event.caster in self.statDict:
                    # self.stat[event.caster][2] += event.damageEff
                    if event.target in self.bld.info.npc:
                        if self.bld.info.getName(event.target) in ["麒麟"]:
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
            if event.content in ['"谁？！别过来！别逼我出手！"']:
                pass
            elif event.content in ['"……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"看招！"']:
                pass
            elif event.content in ['"再接我这招！"']:
                pass
            elif event.content in ['"哈啊！！！"']:
                pass
            elif event.content in ['""']:
                pass
            elif event.content in ['""']:
                pass
            elif event.content in ['""']:
                pass
            elif event.content in ['""']:
                pass
            elif event.content in ['""']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
            if event.id in self.bld.info.npc and self.bld.info.npc[event.id].name in ["麒麟宝箱", "??寶箱"]:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
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
            # print("[Death]", parseTime((event.time - self.startTime) / 1000), event.id, self.bld.info.getName(event.id))
            if self.bld.info.getName(event.id) == "麒麟":
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)

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
        self.activeBoss = "麒麟"
        self.debug = 1

        self.initPhase(1, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["s35558", "b26730", "s35565", "n125008", "n125012", "b26729", "s35570", "b26778",
                                 "s35576", "n125021", "s35596", "b26735", "n125005", "n124876", "n124872", "b26736",
                                 "b26738", "s35564", "s35860", "b26834", "s35579", "s35580", "b26747", "s35573",
                                 "s35819", "n124637", "b26732", "s35568", "n125029", "n125078", "n125711", "s35574",
                                 "s35569", "n125026", "s35700", "n125026", "n124981", "s35582", "s35581", "n125486",
                                 "n125482"
                                 ])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {
                       "c35864": ["4222", "#000000", 1500],  # 雷之呼吸
                       # b26729 电鳞
                       "c35776": ["4222", "#000000", 15000],  # 炙热洪流
                       "c35576": ["4222", "#000000", 5000],  # 擎枫爪
                       "c35975": ["4222", "#000000", 5000],  # 火焰旋涡
                       "c35824": ["4222", "#000000", 5000],  # 雪崩山裂
                       "c35773": ["4222", "#000000", 2000],  # 扫尾
                       "c35819": ["4222", "#000000", 4000],  # 坚鳞利爪
                       "c35573": ["4222", "#000000", 4000],  # 秋风咆哮
                       }

        # 翁幼之数据格式：
        # 7 ？

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {}

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

