"""洛阳之战史朝义：煞将/剑符、红黑煞与后续剑招。"""
from replayer.boss.luoyangzhizhan.EncounterSupport import EncounterReplayer, EncounterWindow


class ShiChaoyiWindow(EncounterWindow):
    TITLE = "洛阳之战·史朝义"
    COLUMNS = (
        ("mainDps", "本体DPS", "对史朝义本体的有效伤害/裁剪后的战斗时间；不含幻象。"),
        ("shaDamage", "煞将伤害", "对煞将的有效伤害总量。"),
        ("swordActivations", "激活剑符", "45521激活剑符技能的实际执行次数，同秒重复事件合并。"),
        ("shadowCalls", "幽影点名", "幽影斩第一、第二、第三顺位点名合计。"),
        ("imbalanceHits", "消融受击", "戾煞消融强/弱受击次数。受击者未必是责任人。"),
        ("invasionMax", "分流最高层", "煞气侵袭最高层数；解包描述只可抵挡三次。"),
    )


class ShiChaoyiReplayer(EncounterReplayer):
    BOSS = "史朝义"
    MAIN_IDS = ("139312", "139365", "138261")
    SHA_IDS = ("139308", "139363", "138323")
    CHEST_IDS = tuple(str(x) for x in range(140063, 140069)) + tuple(str(x) for x in range(140104, 140110))
    SECOND_SKILLS = ("45607", "45682", "45684", "45685", "45686", "45687", "45696", "45697", "45711", "45724")
    THIRD_SKILLS = ("45726", "45727", "45728", "45729", "45737", "45739", "45745", "45746", "45977", "45979", "45981")
    CASTS = {
        "45525": "利刃", "45526": "刃轮", "45530": "杀机", "45535": "煞骸崩陨",
        "45539": "重斩", "45711": "戾芒天坠", "45686": "裂峰斩·一式",
        "45687": "裂峰斩·二式", "45696": "幽影斩", "45724": "戾煞",
        "45726": "连斩·一式", "45729": "连斩·二式", "45739": "啸天",
        "45746": "戾月崩斩", "45977": "坠空斩",
    }
    CALLS = {
        "34115": ("幽影斩·第一顺位", "25359"), "34114": ("幽影斩·第二顺位", "25360"),
        "34113": ("幽影斩·第三顺位", "25361"), "34144": ("啸天点名", "12453"),
        "34156": ("戾月崩斩点名", "12453"), "34543": ("飞行狼牙兵点名", "12453"),
        "34095": ("赤煞", "16371"), "34096": ("幽煞", "16370"),
        "34278": ("携带剑碎片", "16396"),
    }

    def initBattle(self):
        super().initBattle()
        self.initPhase(3, 1)
        self.rewardTime = None
        self.mainExit = None
        self.invasionFailure = set()
        self.shaStart = {}
        self.detail["phaseChanges"] = []
        self.detail["shaPeriods"] = []
        self.detail["phaseEvidence"] = "阶段边界为日志首次出现对应阶段专属招式的时间，可能晚于服务器实际转阶段。三阶段仅按明确的三阶段招式识别。"
        self.detail["mechanicNote"] = "红黑煞消融、分流强爆、煞骸崩陨只记录受击，不将受害者当作责任人。三阶段来自解包配置，9月15日样本尚无三阶段招式；其时长保持0。剑符与煞将阶段仍计有效时间。"
        self.bhBlackList.extend(["s45517", "s45532", "s45607", "s45684", "b34025", "b34027", "b34619"])
        self.bhBlackList.extend("c"+x for x in self.CASTS)
        self.bhBlackList.extend("b"+x for x in self.CALLS)

    def observePhase(self, event):
        if event.dataType not in ("Skill", "Cast") or self.template(event.caster) not in self.MAIN_IDS:
            return
        phase = 3 if event.id in self.THIRD_SKILLS else 2 if event.id in self.SECOND_SKILLS else 0
        if phase > self.phase:
            self.changePhase(event.time, phase)
            self.detail["phaseChanges"].append({"time": event.time, "phase": phase, "skill": event.id})
            label = "本体红黑煞阶段" if phase == 2 else "三阶段剑招"
            self.bh.setEnvironment(event.id, label, "16371", event.time, 0, 1,
                                   "日志首次观测到该阶段招式", "phase", "#9944bb")

    def resolveRewardWin(self):
        # System kill reward + recent main-target damage + immediate main departure.
        # Despawning after a wipe, an unrelated reward, or mere file completion cannot win.
        if (self.rewardTime is not None and self.mainExit is not None
                and self.lastMainDamage is not None
                and 0 <= self.rewardTime-self.lastMainDamage <= 5000
                and 0 <= self.mainExit-self.rewardTime <= 5000):
            self.confirmWin(self.rewardTime, "system_kill_reward_and_main_departure")

    def analyseSecondStage(self, event):
        if self.confirmedEnd is not None and event.time > self.confirmedEnd:
            return
        self.observePhase(event)
        if event.dataType == "Skill":
            self.recordDamage(event, self.MAIN_IDS, "mainDamage")
            self.recordDamage(event, self.SHA_IDS, "shaDamage")
            if event.id == "45521" and event.caster in self.statDict:
                key = (event.caster, "sword")
                if event.time-self.lastHits.get(key, -10**15) >= 1000:
                    self.lastHits[key] = event.time
                    self.increment(event.caster, "swordActivations")
                    self.detail["mechanicEvents"].append({"time": event.time, "kind": "action",
                        "player": self.bld.info.getName(event.caster), "mechanic": "激活剑符", "skill": event.id})
            if event.caster in self.bld.info.npc or event.caster == event.target:
                if event.id in ("45631", "45632"):
                    self.observedHit(event, "imbalanceHits", "戾煞消融")
                elif event.id in ("45705", "45707"):
                    self.observedHit(event, "strongSplitHits", "分流强爆")
                elif event.id == "45537":
                    self.observedHit(event, "shaExplosionHits", "煞骸崩陨")
                elif event.id == "45637":
                    self.observedHit(event, "backlashHits", "煞气反噬")
                elif event.id == "45527":
                    self.observedHit(event, "bladeWheelHits", "刃轮")
        elif event.dataType == "Cast" and self.template(event.caster) in self.MAIN_IDS+self.SHA_IDS:
            if event.id in self.CASTS:
                self.bh.setEnvironment(event.id, self.CASTS[event.id], "16371", event.time, 0, 1,
                                       "首领/煞将运功", "cast", "#bb4444")
        elif event.dataType == "Buff" and event.target in self.statDict:
            if event.id in self.CALLS:
                fresh = self.callBuff(event, *self.CALLS[event.id])
                if fresh and event.id in ("34113", "34114", "34115"):
                    self.increment(event.target, "shadowCalls")
            if event.id == "34057":
                self.stunCounter[event.target].setState(event.time, event.stack > 0)
            elif event.id == "34619":
                stats = self.statDict[event.target]["battle"]
                stats["invasionMax"] = max(stats.get("invasionMax", 0), event.stack)
                if event.stack > 3 and event.target not in self.invasionFailure:
                    self.invasionFailure.add(event.target)
                    self.confirmedFailure(event.target, event.time, "煞气侵袭超过3层",
                                           "34619气劲超过3层；解包描述为只能抵挡三次煞气爆发。")
                elif event.stack == 0:
                    self.invasionFailure.discard(event.target)
        elif event.dataType == "Shout":
            if (str(event.id) == "0" and "洛阳之战" in self.bld.info.map
                    and "侠士完成【击杀25人普通秘境首领】" in event.content
                    and self.lastMainDamage is not None):
                self.rewardTime = event.time
                self.detail["winEvidence"].append({"time": event.time, "rule": "system_kill_reward", "content": event.content})
                self.resolveRewardWin()
        elif event.dataType == "Scene":
            template = self.template(event.id)
            if event.enter and template in self.CHEST_IDS and self.lastMainDamage is not None:
                self.confirmWin(event.time, "boss_chest")
            elif not event.enter and template in self.MAIN_IDS:
                self.mainExit = event.time
                self.resolveRewardWin()
            if template in self.SHA_IDS:
                if event.enter:
                    self.shaStart.setdefault(event.id, event.time)
                    self.bh.setEnvironment(template, "煞将", "16371", event.time, 0, 1, "煞将入场", "npc", "#cc8800")
                else:
                    self.finishSha(event.id, event.time)
        elif event.dataType == "Death":
            if self.template(event.id) in self.MAIN_IDS and self.lastMainDamage is not None:
                self.confirmWin(event.time, "main_npc_death")
            self.finishSha(event.id, event.time)
        super().analyseSecondStage(event)

    def finishSha(self, npc_id, time):
        if npc_id in self.shaStart:
            self.detail["shaPeriods"].append({"start": self.shaStart.pop(npc_id), "end": time})

    def trimTime(self):
        self.resolveRewardWin()
        return super().trimTime()

    def countFinal(self):
        if self.finalized:
            return
        self.finalized = True
        self.resolveRewardWin()
        end = self.encounterEnd()
        for npc_id in list(self.shaStart):
            self.finishSha(npc_id, end)
        self.finishEncounter()
        super().countFinal()
        for phase in range(1, 4):
            self.detail["P%dTime" % phase] = round(self.phaseTime[phase]/1000, 2)
        self.detail["phaseTimes"] = {"煞将/剑符": self.detail["P1Time"], "本体红黑煞": self.detail["P2Time"], "三阶段": self.detail["P3Time"]}
        self.detail["phaseSummary"] = "煞将/剑符 %.1f秒 / 本体红黑煞 %.1f秒 / 三阶段 %.1f秒（首次招式边界）" % (
            self.detail["P1Time"], self.detail["P2Time"], self.detail["P3Time"])
