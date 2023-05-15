# Created by moeheart at 04/15/2022
# 翁幼之的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class WengYouzhiWindow(SpecificBossWindow):
    '''
    翁幼之的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("翁幼之", "1200x800")
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

class WengYouzhiReplayer(SpecificReplayerPro):

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
                        if self.bld.info.getName(event.target) in ["翁幼之"]:
                            self.bh.setMainTarget(event.target)
                            if event.damageEff > 1 and self.immuneStatus == 1:
                                self.bh.setBadPeriod(self.immuneTime, event.time, True, False)
                                self.immuneStatus = 0

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
            if event.content in ['"休想妨碍宗主！"']:
                pass
            elif event.content in ['"豁！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"不自量力。"']:
                pass
            elif event.content in ['"唔！"']:
                pass
            elif event.content in ['"唔！"']:
                pass
            elif event.content in ['"啊……"']:
                pass
            elif event.content in ['"小子鲁莽，不过倒也有些胆气。"']:
                pass
            elif event.content in ['"啊……你们这些匪徒！为何杀我妻儿！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", color="#000000")
                self.immuneStatus = 1
                self.immuneTime = event.time
                self.immuneHealer = 0
            elif event.content in ['"你们……是你们！"']:
                pass
            elif event.content in ['"毁了我的一切！"']:
                pass
            elif event.content in ['"偿命……偿命！"']:
                if self.immuneStatus == 0:
                    self.immuneTime = event.time
                self.immuneStatus = 1
                self.immuneHealer = 0
            elif event.content in ['"尝尽我的痛苦！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", color="#000000")
                if self.immuneStatus == 1:
                    self.bh.setBadPeriod(self.immuneTime, event.time, True, False)
                    self.immuneStatus = 0
            elif event.content in ['"谁也别想…阻止我！"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
            elif event.content in ['"师父！"']:
                pass
            elif event.content in ['"呵！"']:
                pass
            elif event.content in ['"无处可逃！"']:
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
            if event.id == "34535":   # 治疗心法的无效时间
                if self.immuneStatus == 1 and self.immuneHealer == 0:
                    self.immuneHealer = 1
                    self.bh.setBadPeriod(self.immuneTime, event.time, False, True)

                    
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
        self.activeBoss = "翁幼之"

        self.initPhase(3, 1)

        self.immuneStatus = 0
        self.immuneHealer = 0
        self.immuneTime = 0

        self.bhBlackList.extend(["n122740", "s34030", "n122506", "b25602", "s34193", "s34046", "s34190", "b25603",
                                 "s34029", "b25535", "b25501", "b25672", "s34312", "n122721", "b25689", "b25670",
                                 "n122495", "c34043", "n122560", "c34047", "s34044", "n122529", "s34196", "b25500",
                                 "n122533", "b25671", "s34314", "b25690", "s34321", "s34327", "n122503", "s34141",
                                 "s34293", "n122532", "n122505", "s34191", "s34306", "s34325", "n122527", "n122890",
                                 "b26160", "n122644", "n122631", "n122673", "n122652", "n122675", "n122633", "n122611",
                                 "b25846", "b25855", "n122672", "b26061", "n122909", "s34526", "s34711", "b26025",
                                 "s34742", "s34737", "b25685", "b25992", "b26100", "s34974", "n122635", "n122647",
                                 "b25837", "b26029", "b25990", "s32392", "n122720", "n122634", "n122612", "b25785",
                                 "s34794"
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
                       "c34048": ["2021", "#77ff00", 7000],  # 血影碎身
                       "c34046": ["3430", "#0000ff", 7000],  # 血魂裂爪
                       "c34190": ["3452", "#ff0000", 3000],  # 骨刃罡风
                       "c34195": ["3398", "#007700", 2000],   # 断魂流影
                       "c34028": ["3407", "#00ffff", 5000],   # 森罗万刃
                       "c34309": ["4224", "#ff7700", 0],   # 血影坠击
                       "c34313": ["3428", "#7700ff", 5000],   # 黄泉鬼步
                       "c34306": ["2026", "#ff00ff", 3000],   # 血狩孤魂
                       "c34321": ["2024", "#7777ff", 9000],   # 击空断骨
                       "c34291": ["3426", "#ff77cc", 2000],   # 恶鬼噬心
                       "c34563": ["345", "#ff7700", 5000],  # 囚魂心牢
                       "c34535": ["2022", "#773300", 0],  # 痛苦凝聚
                       "c34715": ["3398", "#7777ff", 0],  # 聚魂灭魄
                       "c34701": ["2024", "#7777ff", 9000],  # 恨·击空断骨
                       "c34739": ["3426", "#ff77cc", 2000],  # 仇·恶鬼噬心
                       "c34736": ["3428", "#7700ff", 5000],  # 怨·黄泉鬼步
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

