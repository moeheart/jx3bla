# Created by moeheart at 11/03/2022
# 苏凤楼的定制复盘库。
# 功能待定。

from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.Base import SpecificReplayerPro
from replayer.TableConstructorMeta import TableConstructorMeta
from tools.Functions import *

import tkinter as tk
        
class SuFenglouWindow(SpecificBossWindow):
    '''
    苏凤楼的定制复盘窗口类。
    '''

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        self.constructWindow("苏凤楼", "1200x800")
        window = self.window
        
        frame1 = tk.Frame(window)
        frame1.pack()
        
        #通用格式：
        #0 ID, 1 门派, 2 有效DPS, 3 团队-心法DPS/治疗量, 4 装分, 5 详情, 6 被控时间
        
        tb = TableConstructorMeta(self.config, frame1)

        self.constructCommonHeader(tb, "")
        tb.AppendHeader("外场DPS", "在P1对外场苏凤楼的DPS。\n阶段持续时间：%s" % parseTime(self.detail["wcTime"]))
        tb.AppendHeader("内场1DPS", "在第一个幻境期间，对苏凤楼的DPS。\n阶段持续时间：%s" % parseTime(self.detail["nc1Time"]))
        tb.AppendHeader("内场2DPS", "在第二个幻境期间，对剧毒孢子的DPS。\n阶段持续时间：%s" % parseTime(self.detail["nc2Time"]))
        tb.AppendHeader("内场3DPS", "在第三个幻境期间，对苏凤楼的DPS。\n阶段持续时间：%s" % parseTime(self.detail["nc3Time"]))
        tb.AppendHeader("P2DPS", "在25人英雄难度下，最终阶段的DPS。\n阶段持续时间：%s" % parseTime(self.detail["P2Time"]))
        tb.AppendHeader("心法复盘", "心法专属的复盘模式，只有很少心法中有实现。")
        tb.EndOfLine()

        for i in range(len(self.effectiveDPSList)):
            line = self.effectiveDPSList[i]
            self.constructCommonLine(tb, line)

            tb.AppendContext(int(line["battle"]["wcDPS"]))
            tb.AppendContext(int(line["battle"]["nc1DPS"]))
            tb.AppendContext(int(line["battle"]["nc2DPS"]))
            tb.AppendContext(int(line["battle"]["nc3DPS"]))
            tb.AppendContext(int(line["battle"]["P2DPS"]))

            # 心法复盘
            if line["name"] in self.occResult:
                tb.GenerateXinFaReplayButton(self.occResult[line["name"]], line["name"])
            else:
                tb.AppendContext("")
            tb.EndOfLine()

        self.constructNavigator()

    def __init__(self, config, effectiveDPSList, detail, occResult, analysedBattleData):
        super().__init__(config, effectiveDPSList, detail, occResult, analysedBattleData)

class SuFenglouReplayer(SpecificReplayerPro):

    def countFinal(self):
        '''
        战斗结束时需要处理的流程。包括BOSS的通关喊话和全团脱战。
        '''

        self.countFinalOverall()
        self.changePhase(self.finalTime, 0)
        self.bh.setEnvironmentInfo(self.bhInfo)
        self.bh.printEnvironmentInfo()

        self.detail["wcTime"] = int(self.phaseTime[1] / 1000)
        self.detail["nc1Time"] = int(self.phaseTime[2] / 1000)
        self.detail["nc2Time"] = int(self.phaseTime[3] / 1000)
        self.detail["nc3Time"] = int(self.phaseTime[4] / 1000)
        self.detail["P2Time"] = int(self.phaseTime[5] / 1000)

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
                res["battle"]["wcDPS"] = int(safe_divide(res["battle"]["wcDPS"], self.detail["wcTime"]))
                res["battle"]["nc1DPS"] = int(safe_divide(res["battle"]["nc1DPS"], self.detail["nc1Time"]))
                res["battle"]["nc2DPS"] = int(safe_divide(res["battle"]["nc2DPS"], self.detail["nc2Time"]))
                res["battle"]["nc3DPS"] = int(safe_divide(res["battle"]["nc3DPS"], self.detail["nc3Time"]))
                res["battle"]["P2DPS"] = int(safe_divide(res["battle"]["P2DPS"], self.detail["P2Time"]))
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
                    if self.bld.info.getName(event.target) in ["苏凤楼", "蘇鳳樓"]:
                        if self.bld.info.npc[event.target].templateID in ["112018", "112531"]:
                            # self.bh.setMainTarget(event.target)
                            self.statDict[event.caster]["battle"]["nc3DPS"] += event.damageEff
                        else:
                            self.bh.setMainTarget(event.target)
                            self.statDict[event.caster]["battle"]["wcDPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["凌雪阁杀手", "淩雪閣殺手"]:
                        # self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["nc1DPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["剧毒孢子", "劇毒孢子"]:
                        # self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["nc2DPS"] += event.damageEff
                    elif self.bld.info.getName(event.target) in ["另一个苏凤楼", "另一個蘇鳳樓"]:
                        self.bh.setMainTarget(event.target)
                        self.statDict[event.caster]["battle"]["P2DPS"] += event.damageEff

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

            if event.id == "24540":  # 注视
                if event.stack == 1:
                    self.bh.setCall("24540", "注视", "2028", event.time, 0, event.target, "金戈回澜注视点名")
                    # self.stunCounter[event.target].setState(event.time, 1)
                    # self.stunCounter[event.target].setState(event.time + 1500, 0)

            if event.id == "23846":  # 骤雨
                if event.stack == 1:
                    self.zhouyuStart[event.target] = event.time
                    self.stunCounter[event.target].setState(event.time, 1)
                    self.stunCounter[event.target].setState(event.time + 6000, 0)
                else:
                    self.bh.setCall("23846", "骤雨", "12455", self.zhouyuStart[event.target], event.time - self.zhouyuStart[event.target], event.target, "骤雨寒江点名沉默")
                    self.stunCounter[event.target].setState(event.time, 0)

            if event.id == "24009":  # 战栗
                if event.stack == 1:
                    self.stunCounter[event.target].setState(event.time, 1)
                    self.stunCounter[event.target].setState(event.time + 2000, 0)
                    self.bh.setCall("24009", "战栗", "3435", event.time, 2000, event.target, "南渊扑袭点名定身")

            # if event.id == "23830":  # 共鸣
            #     print("[Gongming]", event.time, event.target, self.bld.info.getName(event.target), event.stack)

            if event.id == "23899":  # 记忆幻境
                if event.stack == 0 and self.nowInner == -1:  # 幻境buff消失，从内场退出
                    self.nowInner = 0
                    self.changePhase(event.time, 0)
                    self.setTimer("phase", event.time + 5000, 1)
                    self.bh.setBadPeriod(event.time, event.time + 5000, True, True)
        elif event.dataType == "Shout":
            if event.content in ['"尝尝这招！"']:
                pass
            elif event.content in ['"……（诡异的笛音传来。）"']:
                pass
            elif event.content in ['"头好痛……发生了什么？"']:
                wasteTime = 5000
                if self.nowInner == 1:
                    wasteTime = 7000
                elif self.nowInner == 2:
                    wasteTime = 15000
                elif self.nowInner == 3:
                    wasteTime = 15000
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                self.bh.setBadPeriod(event.time, event.time + wasteTime, True, True)
                self.changePhase(event.time, 0)
                self.setTimer("phase", event.time + wasteTime, self.nowInner + 1)
                self.nowInner = -1
            elif event.content in ['"果然还有余孽。"']:
                pass
            elif event.content in ['"暂时撤退……反正任务已经达成。"']:
                pass
            elif event.content in ['"怎么回事……刚才是我的记忆……还是幻觉？"']:
                pass
            elif event.content in ['"谢谢各位。"']:
                pass
            elif event.content in ['"如此……依计行事。"']:
                pass
            elif event.content in ['"是。"']:
                pass
            elif event.content in ['"什么人？"']:
                pass
            elif event.content in ['"啧……"']:
                pass
            elif event.content in ['"啊……"']:
                pass
            elif event.content in ['"啊！"']:
                pass
            elif event.content in ['"凤棠……是你……"']:
                if self.bld.info.map != "25人英雄西津渡":
                    self.win = 1
                    self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                    self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
                else:
                    self.changePhase(event.time, 0)
            elif event.content in ['"哥……你醒了。"']:
                pass
            elif event.content in ['"我清醒的时间有限……好多事……李重茂……我要告诉你们……"']:
                pass
            elif event.content in ['"哥，不要怕。我们先回万花谷去治你的伤，我们还有很多的时间。"']:
                pass
            elif event.content in ['"不，还不能走……现在必须立即前去阻止那个姓韩的怪人和那个东瀛人！不能让他们的蛊毒污染水源！"']:
                pass
            elif event.content in ['"那个怪人熔炼出的蛊毒虽然与江河相比如沧海一粟，但若以阴阳术催化毒性，就能在水源中快速扩散，污染大片的土地。"']:
                pass
            elif event.content in ['"不，还不能走……现在必须立即前去阻止……"']:
                pass
            elif event.content in ['"阻止……什么？"']:
                pass
            elif event.content in ['"……"']:
                pass
            elif event.content in ['"哥？"']:
                pass
            elif event.content in ['"休想抢走他！他是我的！"']:
                self.bh.setBadPeriod(self.phaseStart, event.time, True, True)
                self.changePhase(event.time, 5)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"死吧！"']:
                pass
            elif event.content in ['"化为灰烬！"']:
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"不！！！我们的复仇还没结束……我还……不想死……"']:
                self.win = 1
                self.bh.setBadPeriod(event.time, self.finalTime, True, True)
                self.bh.setEnvironment("0", event.content, "340", event.time, 0, 1, "喊话", "shout", "#333333")
            elif event.content in ['"哥哥！你还好吗！这是怎么回事？"']:
                pass
            else:
                self.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")

        elif event.dataType == "Scene":  # 进入、离开场景
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
            if event.id == "32031":
                self.nowInner = 1
            elif event.id == "32032":
                self.nowInner = 2
            elif event.id == "32033":
                self.nowInner = 3
                    
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
        self.activeBoss = "苏凤楼"

        self.initPhase(5, 1)

        self.bhBlackList.extend(["s32199", "s32035", "s32658", "s32037", "n110557", "n110556", "s32829", "s32028",
                                 "b23899", "n110727", "n111990", "n110714", "n110693", "n110692", "n110715", "s32117",
                                 "s32114", "b24540", "n112880", "n110557", "n112915", "n112879", "s32039", "n112014",
                                 "n112006", "n112189", "s32160", "b23884", "n110698", "s32986", "n110918", "s32036",
                                 "n111971", "n110573", "b23796", "s32029", "s32959", "s32030", "s32170", "n111463",
                                 "n110586", "n112018", "s32388", "n112531", "n112446", "n112448", "s32258", "s32266",
                                 "s32265", "b23984", "s32323", "b24007", "b24009", "n112474", "b23846", "b23847",
                                 "c32118", "s32118", "n112519", "n112513", "s32958", "s32263", "s32282"])
        self.bhBlackList = self.mergeBlackList(self.bhBlackList, self.config)

        self.bhInfo = {"c32036": ["3431", "#ff7700", 3000],  # 寒霜剑·霜落斩
                       "c32185": ["335", "#ff00ff", 3000],  # 斩风波
                       "c32031": ["4531", "#0000ff", 0],  # 青冥曲
                       "c32116": ["2028", "#ff0077", 2000],  # 金戈回澜
                       "c32032": ["4532", "#0000ff", 0],  # 叹月调
                       "c32033": ["4534", "#0000ff", 0],  # 留阙引
                       "c32258": ["4529", "#7700ff", 3000],  # 黑星尾击
                       "c32266": ["3398", "#7777ff", 3000],  # 嗟叹怒吼
                       "c32264": ["3396", "#ff77cc", 6000],  # 祸城吐息·长
                       "c32329": ["3396", "#ff77cc", 2000],  # 祸城吐息·短
                       "c32285": ["3426", "#0077ff", 7000],  # 南渊扑袭
                       }

        # 苏凤楼数据格式：
        # 7 ？

        self.zhouyuStart = {}
        self.nowInner = -1

        for line in self.bld.info.player:
            self.statDict[line]["battle"] = {"wcDPS": 0,
                                             "nc1DPS": 0,
                                             "nc2DPS": 0,
                                             "nc3DPS": 0,
                                             "P2DPS": 0}
            self.zhouyuStart[line] = 0

    def __init__(self, bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint, config):
        '''
        对类本身进行初始化。
        '''
        super().__init__(bld, occDetailList, startTime, finalTime, battleTime, bossNamePrint)
        self.config = config

