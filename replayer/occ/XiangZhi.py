# Created by moeheart at 09/12/2021
# 奶歌复盘pro，用于奶歌复盘的生成、展示。

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory
from BossNameUtils import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment

import time
import json

XIANGZHI_QIXUE = {
    '14237':'雪海',
    '14247':'太和',
    '23313':'枕流',
    '24020':'流音',
    '14405':'谪仙',
    '14384':'自赏',
    '14406':'寸光阴',
    '26728':'诗上',
    '14244':'凝绝',
    '14359':'棋宫',
    '14242':'掷杯',
    '19308':'思议',
    '14238':'红隙',
    '14373':'秋鸿',
    '17521':'争簇',
    '14439':'织心',
    '14164':'超然',
    '14361':'引芳',
    '14313':'井仪',
    '22029':'绝唱',
    '14163':'相依',
    '14557':'贯珠',
    '18718':'凝眉',
    '22030':'无尽藏',
    '14464':'蔚风',
    '18382':'风入松',
    '14286':'洞天',
    '14285':'殊曲',
    '14248':'寒酒',
    '14253':'犹香',
    '14251':'笙簧',
    '22797':'蒹葭',
    '14461':'鸣鸾',
    '14167':'寿生',
    '14155':'剡注',
    '14442':'桑柔',
    '14256':'石间意',
    '14169':'一指回鸾',
    '14254':'温语',
    '14249':'平吟',
    '23678':'乐情',
    '14874':'捣衣',
    '14470':'天音知脉',
    '18819':'庄周梦',
    '22808':'大韶',
    '15068':'琴音共鸣',
    '26772':'行云',
    '25234':'绕梁',
    '25235':'不器',
    '25236':'古道',
    '25229':'游太清',
}

def getXiangZhiQixue(id):
    '''
    根据ID获取奶歌奇穴名.
    '''
    if id in XIANGZHI_QIXUE:
        return XIANGZHI_QIXUE[id]
    else:
        return "未知"

class ShieldCounterNew(BuffCounter):
    '''
    盾的统计类.
    继承buff的统计类，加入获得次数、破盾次数等指标.
    '''

    def inferFirst(self):
        '''
        根据记录尝试推导战斗开始前是否存在盾，若存在则强制修改最开始的情形为有盾.
        '''
        if len(self.log) > 1 and self.log[1][1] == 0:
            self.log[0][1] = 1

    def countCast(self):
        '''
        计算盾施放的次数.
        根据buff做推断，消失间隔小于500ms的视为没有消失.
        returns:
        - num 盾施放的次数.
        '''
        num = 0
        lastTime = 0
        lastStack = 0
        for line in self.log:
            if line[1] == 1 and lastStack == 0 and line[0] - lastTime > 500:
                num += 1
            lastTime = line[0]
            lastStack = line[1]
        return num

    def countBreak(self):
        '''
        计算破盾的次数.
        直接通过施放的次数推导.
        returns:
        - num 破盾的次数.
        '''
        num = self.countCast()
        if self.checkState(self.finalTime) == 1:
            num -= 1
        return num

    def __init__(self, shieldLog, startTime, finalTime):
        '''
        初始化.
        '''
        super().__init__(shieldLog, startTime, finalTime)

class SkillLogCounter():
    '''
    技能统计类.
    TODO: 扩展这个类的功能，支持更多统计.
    '''
    skillLog = []
    actLog = []
    startTime = 0
    finalTime = 0
    speed = 3770
    sumBusyTime = 0
    sumSpareTime = 0

    def getLength(self, length):
        flames = calculFramesAfterHaste(self.speed, length)
        return flames * 0.0625 * 1000

    def analysisSkillData(self):
        for line in self.skillLog:
            if line[1] in [15181, 15082, 25232]:  #奶歌常见的自动施放技能：影子宫，影子宫，桑柔
                continue
            elif line[1] in [14137, 14300]:  # 宫，变宫
                self.actLog.append([line[0] - self.getLength(24), self.getLength(24)])
            elif line[1] in [14140, 14301]:  # 徵，变徵
                self.actLog.append([line[0] - self.getLength(16), self.getLength(16)])
            else:
                self.actLog.append([line[0], self.getLength(24)])

        self.actLog.sort(key=lambda x: x[0])

        nowTime = self.startTime
        self.sumBusyTime = 0
        self.sumSpareTime = 0
        for line in self.actLog:
            if line[0] > nowTime:
                self.sumSpareTime += line[0] - nowTime
                self.sumBusyTime += line[1]
                nowTime = line[0] + line[1]
            elif line[0] + line[1] > nowTime:
                self.sumBusyTime += line[0] + line[1] - nowTime
                nowTime = line[0] + line[1]

    def __init__(self, skillLog, startTime, finalTime, speed=3770):
        self.skillLog = skillLog
        self.actLog = []
        self.startTime = startTime
        self.finalTime = finalTime
        self.speed = speed

class XiangZhiProReplayer(ReplayerBase):
    '''
    奶歌复盘pro类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶歌复盘pro v%s"%EDITION
        self.result["overall"]["playerID"] = "未知"
        self.result["overall"]["server"] = self.bld.info.server
        self.result["overall"]["battleTime"] = self.bld.info.battleTime
        self.result["overall"]["battleTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        self.result["overall"]["generateTime"] = time.time()
        self.result["overall"]["generateTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["generateTime"]))
        self.result["overall"]["map"] = self.bld.info.map
        self.result["overall"]["boss"] = getNickToBoss(self.bld.info.boss)
        self.result["overall"]["sumTime"] = self.bld.info.sumTime
        self.result["overall"]["sumTimePrint"] = parseTime(self.bld.info.sumTime / 1000)
        self.result["overall"]["dataType"] = self.bld.dataType

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"', '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
                self.npcKey = key
                break

        # 记录盾的存在情况与减疗
        shieldLogDict = {}
        jianLiaoLog = {}

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.
        self.interrupt = 0

        # 不知道有什么用
        self.activeBoss = ""

        # 记录战斗开始时间与结束时间
        self.startTime = self.bld.log[0].time
        self.finalTime = self.bld.log[-1].time

        # 记录所有治疗的key，首先尝试直接使用心法列表获取.
        self.healerDict = {}
        XiangZhiList = []

        # 记录具体心法的表.
        occDetailList = {}
        for key in self.bld.info.player:
            occDetailList[key] = self.bld.info.player[key].occ

        self.shieldCountersNew = {}
        for key in self.bld.info.player:
            self.shieldCountersNew[key] = ShieldCounterNew("16911", self.startTime, self.finalTime)

        for event in self.bld.log:
            # if self.startTime == 0:
            #     self.startTime = event.time
            # self.finalTime = event.time

            if self.interrupt != 0:
                continue

            if event.dataType == "Skill":
                # 记录奶歌和治疗心法的出现情况.
                if event.caster not in XiangZhiList and event.id in ["14231", "14140", "14301"]:  # 奶歌的特征技能
                    XiangZhiList.append(event.caster)
                    self.healerDict[event.caster] = 0
                if event.caster not in self.healerDict and event.id in ["565", "554", "555", "2232", "6662", "2233", "6675",
                                                                  "2231", "101", "142", "138", "16852", "18864"]:  # 其它治疗的特征技能
                    self.healerDict[event.caster] = 0

                # 记录主动贴盾，主要是为了防止复盘记录中的数据丢失。
                if event.id == "14231":
                    jianLiaoStack = 0
                    if event.target in jianLiaoLog:
                        jianLiaoStack = jianLiaoLog[event.target].checkState(event.time)
                    if jianLiaoStack < 20:
                        if event.target not in shieldLogDict:
                            shieldLogDict[event.target] = []
                        shieldLogDict[event.target].append([event.time, 1])
                        self.shieldCountersNew[event.target].setState(event.time, 1)

                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"宓桃"':
                    self.activeBoss = "宓桃"
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif event.dataType == "Buff":
                if event.id in ["9334", "16911"]:  # buff梅花三弄
                    if event.target not in shieldLogDict:
                        shieldLogDict[event.target] = []
                    shieldLogDict[event.target].append([event.time, event.stack])
                    self.shieldCountersNew[event.target].setState(event.time, event.stack)
                if event.id in ["15774", "17200"]:  # buff精神匮乏
                    if event.target not in jianLiaoLog:
                        jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                    jianLiaoLog[event.target].setState(event.time, event.stack)
                if event.caster in occDetailList and occDetailList[event.caster] in ['21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                # 为未来需要统计喊话时备用.
                pass

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        for key in self.bld.info.player:
            self.shieldCountersNew[key].inferFirst()

        #TODO 移除
        #self.myname = "今夏草木长"

        # 自动推导奶歌角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            if len(XiangZhiList) >= 2:
                nameList = []
                for line in XiangZhiList:
                    nameList.append(namedict[line][0])
                s = str(nameList)
                raise Exception('奶歌的数量不止一个，请手动指示ID。可能的ID为：%s' % s)
            elif len(XiangZhiList) == 0:
                raise Exception('没有找到奶歌，请确认数据是否正确')
            else:
                self.mykey = XiangZhiList[0]
                self.myname = self.bld.info.player[self.mykey].name
                print("自动推断奶歌角色名为：%s"%self.myname)
        else:
            for key in self.bld.info.player:
                if self.bld.info.player[key].name == self.myname:
                    self.mykey = key

        self.occDetailList = occDetailList

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        # TODO 实现
        self.result["equip"] = {"available": 0}
        if self.bld.info.player[self.mykey].equip != {}:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, "22h")
            self.result["equip"]["score"] = self.bld.info.player[self.mykey].equipScore
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["spirit"] = res["根骨"]
            self.result["equip"]["heal"] = res["治疗"]
            self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["critPercent"] = res["会心"]
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = res["会效"]
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["hastePercent"] = res["加速"]
            self.result["equip"]["haste"] = res["加速等级"]
            self.haste = self.result["equip"]["haste"]

        self.result["qixue"] = {"available": 0}
        if self.bld.info.player[self.mykey].qx != {}:
            self.result["qixue"]["available"] = 1
            for key in self.bld.info.player[self.mykey].qx:
                self.result["qixue"][key] = getXiangZhiQixue(self.bld.info.player[self.mykey].qx[key]["2"])

        print(self.result["overall"])
        print(self.result["equip"])
        print(self.result["qixue"])

        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        occDetailList = self.occDetailList

        #data = XiangZhiData()

        num = 0
        skillLog = []

        # 以承疗者记录的关键治疗
        self.criticalHealCounter = {}
        hpsActive = 0

        # 以治疗者记录的关键治疗
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            numSmall = 0

        # TODO 简化，删除无用的统计信息
        numHeal = 0
        numEffHeal = 0
        numAbsorb = 0
        npcHealStat = {}
        numPurge = 0 # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害]
        damageDict = {}  # 伤害统计
        # myDamageRank = 0  # 个人伤害排名
        # myDamage = 0  # 个人伤害
        healStat = {}  # 治疗统计
        # healList = {}  # list形式的治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        # healRate = 0  # 治疗占比
        rateDict = {}  # 盾覆盖率
        # durationDict = {}  # 盾持续时间
        breakDict = {}  # 破盾次数
        sumShield = 0  # 盾数量
        # equalDPS = 0  # 强度，相当于几个DPS
        # overallRate = 0  # 盾的整体覆盖率

        # 技能统计
        mhsnSkill = SkillCounter("14231", self.startTime, self.finalTime, self.haste)  # 梅花三弄
        gongSkill = SkillHealCounter("14137", self.startTime, self.finalTime, self.haste)  # 宫
        zhiSkill = SkillHealCounter("14140", self.startTime, self.finalTime, self.haste)  # 徵
        yuSkill = SkillHealCounter("14141", self.startTime, self.finalTime, self.haste)  # 羽
        shangSkill = SkillHealCounter("14138", self.startTime, self.finalTime, self.haste)  # 商
        jueSkill = SkillHealCounter("14139", self.startTime, self.finalTime, self.haste)  # 角
        shangBuff = SkillHealCounter("9459", self.startTime, self.finalTime, self.haste)  # 商
        jueBuff = SkillHealCounter("9463", self.startTime, self.finalTime, self.haste)  # 角
        xySkill = SkillHealCounter("21321", self.startTime, self.finalTime, self.haste)  # 相依
        shangBuffDict = {}
        jueBuffDict = {}
        for line in self.bld.info.player:
            shangBuffDict[line] = BuffCounter("9459", self.startTime, self.finalTime) # 商，9460=殊曲，9461=洞天
            jueBuffDict[line] = BuffCounter("9463", self.startTime, self.finalTime) # 角，9460=殊曲，9461=洞天
        lastSkillTime = self.startTime

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        bhSkill = "0"
        bhTimeStart = 0
        bhTimeEnd = 0
        bhNum = 0
        bhHeal = 0
        bhHealEff = 0
        bhDelay = 0
        bhDelayNum = 0
        skillNameDict = {"0": "未知",
                         "14231": "梅花三弄",
                         "14137": "宫",
                         "14300": "宫",
                         "14140": "徵",
                         "14362": "徵",
                         "14301": "徵",
                         "14141": "羽",
                         "14354": "羽",
                         "14138": "商",
                         "14139": "角"}
        skillIconDict = {"0": "未知",
                         "14231": "7059",
                         "14137": "7171",
                         "14300": "7171",
                         "14140": "7174",
                         "14362": "7174",
                         "14301": "7174",
                         "14141": "7175",
                         "14354": "7175",
                         "14138": "7172",
                         "14139": "7173"}
        xiangZhiUnimportant = ["15181", "15082", "25232",  # 影子宫，桑柔
                               "4877", "15054", "15057",  # 水特效作用，盾奇穴效果
                               "25683", "24787",  # 破招
                               "22155", "22207",  # 大附魔
                               "14535", "14532", "18865", # 徵判定
                               "3071", "18274", "14646",  # 治疗套装，寒清，书离
                               "23951", # 贯体通用
                               "15168", "14357", "14355", "15169", # 羽
                               "14399", # 角判定
                               "14395", # 商判定
                               "14536", "14537", # 盾填充, 盾移除
                               "15138", "15081", "15153", # 影子判定
                               "25237", # 古道
                               "14071", # 盾主动切换技能
                              ]
        xiangZhiSpecial = ["20763", "20764", "21321",  # 相依
                           "15039", # 传影子
                           "14150", # 云生结海
                           "14075",  # 云生结海主动
                           "18838", # 梅花切高山
                           "18841", # 高山切梅花
                           "14069", # 高山
                           "14076", # 青霄飞羽
                           "21324", # 青霄飞羽·落
                           "14081", # 孤影施放
                           ]

        for event in self.bld.log:
            if event.time > self.finalTime:
                break

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    numAbsorb += event.healEff
                else:
                    # 所有治疗技能都不计算化解.
                    # 统计自身治疗
                    if event.caster == self.mykey and event.heal != 0:
                        numHeal += event.heal
                        numEffHeal += event.healEff

                    # 统计团队治疗
                    if event.heal + event.healEff > 0 and event.effect != 7 and event.caster in self.healerDict:
                        if event.caster not in healStat:
                            healStat[event.caster] = [0, 0]
                        healStat[event.caster][0] += event.healEff
                        healStat[event.caster][1] += event.heal

                    # 统计自身技能使用情况. TODO: 扩展为每个技能分别处理
                    if event.caster == self.mykey and event.scheme == 1 and event.id not in xiangZhiUnimportant: # 影子宫、桑柔等需要过滤的技能
                        skillLog.append([event.time, event.id])
                        # 若技能没有连续，则在战斗回放中记录技能
                        if (event.id not in skillNameDict or skillNameDict[event.id] != skillNameDict[bhSkill]) and event.id not in xiangZhiSpecial:
                            # 记录本次技能
                            # print(event.id, bhSkill)
                            if bhSkill != "0":
                                bh.setNormalSkill(bhSkill, skillNameDict[bhSkill], skillIconDict[bhSkill],
                                                  bhTimeStart, bhTimeEnd - bhTimeStart, bhNum, bhHeal,
                                                  roundCent(bhHealEff / (bhHeal + 1e-10)),
                                                  int(bhDelay / (bhDelayNum + 1e-10)), "")
                            bhSkill = "0"
                            bhTimeStart = 0
                            bhNum = 0
                            bhHeal = 0
                            bhHealEff = 0
                            bhDelay = 0
                            bhDelayNum = 0
                        if bhSkill == "0" and event.id in skillNameDict:
                            bhSkill = event.id
                            bhTimeStart = event.time  # 并非最终结果，对于读条技能可能会修正
                        # 分技能进行处理
                        if event.id in ["14231"]:  # 梅花三弄
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            lastSkillTime = mhsnSkill.recordSkill(event.time, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14137", "14300"]:  # 宫
                            if bhNum == 0:
                                bhTimeStart -= getLength(24, self.haste)
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime - getLength(24, self.haste)
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = gongSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14362"]:  # 徵实际效果
                            if bhNum == 0:
                                bhTimeStart -= getLength(8, self.haste)
                            if event.time - lastSkillTime > getLength(8, self.haste) + 100:
                                bhNum += 1
                                bhDelayNum += 1
                                bhDelay += event.time - lastSkillTime - getLength(8, self.haste)
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = zhiSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14141"]:  # 羽
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = yuSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["21321"]:  # 相依
                            # TODO 实现特殊技能处理
                            xySkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        elif event.id in ["14138"]:  # 商
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = shangSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                        elif event.id in ["14139"]:  # 角
                            bhNum += 1
                            bhDelayNum += 1
                            bhDelay += event.time - lastSkillTime
                            bhHeal += event.heal
                            bhHealEff += event.healEff
                            lastSkillTime = jueSkill.recordSkill(event.time, event.heal, event.healEff, lastSkillTime) + getLength(24, self.haste)
                            bhTimeEnd = lastSkillTime
                        else:
                            pass
                            # 对于其它的技能暂时不做记录
                            # lastSkillTime = event.time

                    if event.caster == self.mykey and event.scheme == 2:
                        if event.id in ["9459", "9460", "9461", "9462"]:  # 商
                            shangBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                        elif event.id in ["9463", "9464", "9465", "9466"]:  # 角
                            jueBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

                    # 统计对NPC的治疗情况.
                    if event.healEff > 0 and event.target == self.npcKey:
                        if event.caster not in npcHealStat:
                            npcHealStat[event.caster] = 0
                        npcHealStat[event.caster] += event.healEff

                    # 统计以承疗者计算的关键治疗
                    if event.healEff > 0 and self.npcKey != 0:
                        if event.target in self.criticalHealCounter and self.criticalHealCounter[event.target].checkState(event.time):
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = event.healEff
                            else:
                                npcHealStat[event.caster] += event.healEff

                    # 统计以治疗者计算的关键治疗
                    if self.activeBoss in ["宓桃", "哑头陀"]:
                        if event.healEff > 0 and self.npcKey != 0 and hpsActive:
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = 0
                            npcHealStat[event.caster] += event.healEff

                    if event.id == "14169":  # 一指回鸾
                        numPurge += 1

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.shieldCountersNew:
                        if event.caster not in battleStat:
                            battleStat[event.caster] = [0, 0, 0]  # 无盾伤害，有盾伤害，桑柔伤害
                        if int(event.id) >= 21827 and int(event.id) <= 21831:  # 桑柔
                            battleStat[event.caster][2] += event.damageEff
                        elif event.id == "25232" and event.caster == self.mykey:  # 桑柔伤害
                            battleStat[event.caster][2] += event.damageEff
                        else:
                            hasShield = self.shieldCountersNew[event.caster].checkState(event.time)
                            battleStat[event.caster][hasShield] += event.damageEff

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["9459", "9460", "9461", "9462"]:  # 商
                    shangBuffDict[event.target].setState(event.time, event.stack)
                if event.id in ["9463", "9464", "9465", "9466"]:  # 角
                    jueBuffDict[event.target].setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                pass

            num += 1

        # 记录最后一个技能
        if bhSkill != "0":
            bh.setNormalSkill(bhSkill, skillNameDict[bhSkill], skillIconDict[bhSkill],
                              bhTimeStart, bhTimeEnd - bhTimeStart, bhNum, bhHeal,
                              roundCent(bhHealEff / (bhHeal + 1e-10)),
                              int(bhDelay / (bhDelayNum + 1e-10)), "")

        # 计算战斗效率等统计数据，TODO 扩写
        skillCounter = SkillLogCounter(skillLog, self.startTime, self.finalTime, self.haste)
        skillCounter.analysisSkillData()
        sumBusyTime = skillCounter.sumBusyTime
        sumSpareTime = skillCounter.sumSpareTime
        spareRate = sumSpareTime / (sumBusyTime + sumSpareTime + 1e-10)

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

        # 计算等效伤害
        numdam1 = 0
        for key in battleStat:
            # if int(occdict[key][0]) == 0:
            #     continue
            line = battleStat[key]
            # damageDict[key] = line[0] + line[1] / 1.117 # 100赛季数值
            # numdam1 += line[1] / 1.117 * 0.117# + line[2]
            damageDict[key] = line[0] + line[1] / 1.0554  # 110赛季数值
            numdam1 += line[1] / 1.0554 * 0.0554
        if self.mykey in battleStat:
            numdam2 = battleStat[self.mykey][2]
        else:
            numdam2 = 0
        numdam = numdam1 + numdam2

        # 关键治疗量统计
        if self.activeBoss in ["宓桃", "哑头陀"]:
            for line in npcHealStat:
                npcHealStat[line] /= (hpsSumTime + 1e-10)

        # print("[测试]治疗量：", numHeal)
        # print("[测试]有效治疗量：", numEffHeal)
        # print("[测试]化解：", numAbsorb)
        # for line in rateDict:
        #     print(line, rateDict[line], breakDict[line])
        # print(sumShield)

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0}
        healList = dictToPairs(healStat)
        healList.sort(key=lambda x: -x[1][0])

        sumHeal = 0
        numid = 0
        topHeal = 0
        for line in healList:
            if numid == 0:
                topHeal = line[1][0]
            sumHeal += line[1][0]
            numid += 1
            if line[0] == self.mykey and myHealRank == 0:
                myHealRank = numid
            # 当前逻辑为治疗量大于第一的20%才被记为治疗，否则为老板
            if line[1][0] > topHeal * 0.2:
                numHealer += 1
        if myHealRank > numHealer:
            numHealer = myHealRank
        self.result["healer"]["numHealer"] = numHealer
        for line in healList:
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "healEff": int(line[1][0] / self.bld.info.sumTime * 1000),
                   "heal": int(line[1][1] / self.bld.info.sumTime * 1000)}
            self.result["healer"]["table"].append(res)

        # 计算DPS列表(Part 7)
        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        for key in self.shieldCountersNew:
            sumShield += self.shieldCountersNew[key].countCast()
            # 过滤老板，T奶，自己
            if key not in damageDict or damageDict[key] / self.result["overall"]["sumTime"] * 1000 < 10000:
                continue
            if occDetailList[key] in ["1t", "2h", "3t", "5h", "10t", "6h", "21t", "22h"]:
                continue
            if key == self.mykey:
                continue
            time1 = self.shieldCountersNew[key].buffTimeIntegral()
            timeAll = self.shieldCountersNew[key].sumTime()
            rateDict[key] = time1 / timeAll
            breakDict[key] = self.shieldCountersNew[key].countBreak()

        for line in damageList:
            if line[0] not in rateDict:
                continue
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.bld.info.sumTime * 1000),
                   "shieldRate": roundCent(rateDict[line[0]]),
                   "shieldBreak": breakDict[line[0]]}
            self.result["dps"]["table"].append(res)

        # 计算覆盖率
        numRate = 0
        sumRate = 0
        for key in rateDict:
            numRate += 1
            sumRate += rateDict[key]
        overallRate = sumRate / (numRate + 1e-10)

        # 计算技能统计
        self.result["skill"] = {}
        # 梅花三弄
        self.result["skill"]["meihua"] = {}
        self.result["skill"]["meihua"]["num"] = mhsnSkill.getNum()
        self.result["skill"]["meihua"]["delay"] = int(mhsnSkill.getAverageDelay())
        self.result["skill"]["meihua"]["cover"] = roundCent(overallRate)
        # 宫
        self.result["skill"]["gong"] = {}
        self.result["skill"]["gong"]["num"] = gongSkill.getNum()
        self.result["skill"]["gong"]["delay"] = int(gongSkill.getAverageDelay())
        effHeal = gongSkill.getHealEff()
        self.result["skill"]["gong"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["gong"]["effRate"] = effHeal / (gongSkill.getHeal() + 1e-10)
        # 徵
        self.result["skill"]["zhi"] = {}
        self.result["skill"]["zhi"]["num"] = zhiSkill.getNum()
        self.result["skill"]["zhi"]["delay"] = int(zhiSkill.getAverageDelay())
        effHeal = zhiSkill.getHealEff()
        self.result["skill"]["zhi"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["zhi"]["effRate"] = roundCent(effHeal / (zhiSkill.getHeal() + 1e-10))
        # 羽
        self.result["skill"]["yu"] = {}
        self.result["skill"]["yu"]["num"] = yuSkill.getNum()
        self.result["skill"]["yu"]["delay"] = int(yuSkill.getAverageDelay())
        effHeal = yuSkill.getHealEff()
        self.result["skill"]["yu"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["yu"]["effRate"] = roundCent(effHeal / (yuSkill.getHeal() + 1e-10))
        # 商，注意Buff与Skill统计不同
        self.result["skill"]["shang"] = {}
        self.result["skill"]["shang"]["num"] = shangBuff.getNum()
        self.result["skill"]["shang"]["delay"] = int(shangSkill.getAverageDelay())
        effHeal = shangBuff.getHealEff()
        self.result["skill"]["shang"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        num = 0
        sum = 0
        for key in shangBuffDict:
            singleDict = shangBuffDict[key]
            num += 1
            sum += singleDict.buffTimeIntegral() / singleDict.sumTime()
        self.result["skill"]["shang"]["cover"] = roundCent(sum / (num + 1e-10))
        # 角
        self.result["skill"]["jue"] = {}
        self.result["skill"]["jue"]["num"] = jueBuff.getNum()
        self.result["skill"]["jue"]["delay"] = int(jueSkill.getAverageDelay())
        effHeal = jueBuff.getHealEff()
        self.result["skill"]["jue"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        num = 0
        sum = 0
        for key in jueBuffDict:
            singleDict = jueBuffDict[key]
            num += 1
            sum += singleDict.buffTimeIntegral() / singleDict.sumTime()
        self.result["skill"]["jue"]["cover"] = roundCent(sum / (num + 1e-10))
        # 相依
        self.result["skill"]["xiangyi"] = {}
        self.result["skill"]["xiangyi"]["num"] = xySkill.getNum()
        effHeal = xySkill.getHealEff()
        self.result["skill"]["xiangyi"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["xiangyi"]["effRate"] = roundCent(effHeal / (xySkill.getHeal() + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
        self.result["skill"]["general"]["SangrouDPS"] = int(numdam2 / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["general"]["ZhuangzhouDPS"] = int(numdam1 / self.result["overall"]["sumTime"] * 1000)

        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay()

        print(self.result["healer"])
        print(self.result["dps"])
        print(self.result["skill"])
        #print(self.result["replay"])
        for line in self.result["replay"]["normal"]:
            print(line)

    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        pass


    def replay(self):
        '''
        开始奶歌复盘pro分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", battleDate=""):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        '''
        #self.battleDate = battleDate
        #self.win = 0
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.myname = myname
        self.failThreshold = config.failThreshold
        self.mask = config.mask
        self.filePath = path + '\\' + fileNameInfo[0]
        self.bld = bldDict[fileNameInfo[0]]

        self.result = {}
        self.haste = 8780  # TODO: 在属性计算完成后修改


        #if self.numTry == 0:
        #    self.bossNamePrint = self.bossname
        #else:
        #    self.bossNamePrint = "%s.%d" % (self.bossname, self.numTry)

        print("奶歌复盘pro类创建成功...")

