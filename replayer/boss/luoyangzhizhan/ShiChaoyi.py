"""洛阳之战史朝义：煞将/剑符、红黑煞与后续剑招。"""
from replayer.boss.luoyangzhizhan.EncounterSupport import EncounterReplayer, EncounterWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import record_shout, finalize_phase_periods, record_environment
from replayer.boss.luoyangzhizhan.Timeline import STYLES, tag_source
from replayer.boss.luoyangzhizhan.TransitionEvidence import TransitionAvailability


class ShiChaoyiWindow(EncounterWindow):
    TITLE = "洛阳之战·史朝义"
    COLUMNS = (
        ("mainDps", "本体DPS", "对史朝义本体的有效伤害/输出有效时间；扣除已确认无目标的煞甲归身转场，不含幻象。"),
        ("shaDamage", "煞将伤害", "对煞将的有效伤害总量。"),
        ("flyingDamage", "飞兵伤害", "对飞行狼牙兵139918的有效伤害总量，不计入本体伤害。"),
        ("swordActivations", "激活剑符", "45521激活剑符技能的实际执行次数，同秒重复事件合并。"),
        ("fragmentPickups", "拾取碎片", "34278碎片气劲层数增加量；刷新不累计，移除不视为交付。"),
        ("wingCalls", "获得翅膀", "34324翅膀气劲的新获得次数，不累计刷新。"),
        ("shadowCalls", "幽影点名", "幽影斩第一、第二、第三顺位点名合计。"),
        ("imbalanceHits", "消融受击", "戾煞消融强/弱受击次数。受击者未必是责任人。"),
        ("invasionMax", "分流最高层", "煞气侵袭最高层数；解包描述只可抵挡三次。"),
    )


class ShiChaoyiReplayer(EncounterReplayer):
    BOSS = "史朝义"
    MAIN_IDS = ("139312", "139365", "138261")
    SHA_IDS = ("139308", "139363", "138323")
    FLYING_IDS = ("139918",)
    SWORD_IDS = ("138287",)
    LIFU_IDS = ("139332", "139388")
    CHEST_IDS = tuple(str(x) for x in range(140063, 140069)) + tuple(str(x) for x in range(140104, 140110))
    SECOND_SKILLS = ("45607", "45682", "45684", "45685", "45686", "45687", "45696", "45697", "45711", "45724")
    THIRD_SKILLS = ("45726", "45727", "45728", "45729", "45737", "45739", "45745", "45746", "45977", "45979", "45981")
    CASTS = {
        "45525": "利刃", "45526": "刃轮", "45530": "杀机", "45535": "煞骸崩陨",
        # 45539 is a frequent 煞将 rectangular cleave, omitted from the raid
        # summary axis; its native events and damage still pass through.
        "45711": "戾芒天坠", "45686": "裂峰斩·一式",
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
        "34324": ("翅膀飞行", "1485"),
    }

    TRANSITION_START = "此痛朕记下了，煞…甲…归…身！"
    TRANSITION_END = "狂妄的唐廷贼子！让你们见识一下真正的帝煞威仪！"
    SHOUTS = {
        "尔等命数到此！": "杀机", "暂留尔等残命！": "杀机结束",
        "利刃出鞘！": "利刃", "刀锋噬骨！": "刃轮",
        TRANSITION_START: "煞甲归身转场", TRANSITION_END: "帝煞威仪宣言",
        "万…煞…奔…流！": "戾芒天坠",
        "朕先斩你！哈！一刀断命！": "裂峰斩",
        "一斩…索命！": "幽影斩", "尔等，罪当伏诛": "戾煞",
        "分光化影！": "戾月崩斩", "百刺穿心，血尽方休！": "连斩",
        "刀芒惊天！": "啸天", "自天而刑，诛逆！": "坠空斩",
        "朕即大燕，睥见天命！": "天命宣言",
    }
    LIFU_SHOUTS = {
        "诸位，我会以内力凝成三道“玄天剑符”。速速催动剑符，结成“玄天阵”便可对抗帝煞之气！": "玄天剑符",
        "速将散落的“残刃”聚拢于我，我要以内力重铸此剑！": "重铸残刃",
    }

    def initBattle(self):
        super().initBattle()
        self.initPhase(3, 1)
        self.rewardTime = None
        self.mainExit = None
        self.invasionFailure = set()
        self.invasionStacks = []
        self.shaStart = {}
        self.fragmentStacks = {}
        self.transitionStart = None
        self.transitionAvailability = TransitionAvailability(
            self.startTime, self.SHA_IDS + self.SWORD_IDS + self.FLYING_IDS)
        self.detail["transitionPeriods"] = []
        self.detail["phaseChanges"] = []
        self.detail["shaPeriods"] = []
        self.detail["phaseEvidence"] = "二阶段优先使用本体煞甲归身喊话，缺失时回退首次阶段专属招式。仅双本体转场喊话完整、前阶段目标均已退场且候选区间没有有效伤害时扣除输出时间；治疗时间保留，不向喊话外的无伤害空窗延伸。三阶段仅按明确专属招式识别。"
        self.detail["mechanicNote"] = "飞行狼牙兵伤害单列；拾取碎片按34278增层统计，不把移除当作交付。红黑煞消融、分流强爆、煞骸崩陨只记录受击。剑符、煞将尚在场时保持有效；重铸期间仍有可攻击本体和飞兵，不能整段扣除。煞甲归身只扣已确认无目标区间的输出时间，治疗仍有效。"
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
        self.observeCombatEnd(event)
        self.transitionAvailability.observe(event, self.bld.info)
        self.observePhase(event)
        if event.dataType == "Skill":
            self.recordReflectedDamage(event, {
                "mainDamage": self.MAIN_IDS, "shaDamage": self.SHA_IDS,
                "flyingDamage": self.FLYING_IDS,
            })
            self.recordDamage(event, self.MAIN_IDS, "mainDamage")
            self.recordDamage(event, self.SHA_IDS, "shaDamage")
            self.recordDamage(event, self.FLYING_IDS, "flyingDamage")
            if event.id == "45521" and event.caster in self.statDict:
                key = (event.caster, "sword")
                if event.time-self.lastHits.get(key, -10**15) >= 1000:
                    self.lastHits[key] = event.time
                    self.increment(event.caster, "swordActivations", time=event.time)
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
                elif event.id == "46077":
                    self.observedHit(event, "windBladeHits", "高空风刃")
        elif event.dataType == "Cast" and self.template(event.caster) in self.MAIN_IDS+self.SHA_IDS:
            if event.id in self.CASTS:
                label = self.CASTS[event.id]
                record_environment(self, event, {('Cast', event.id): (label, *STYLES[label])})
        elif event.dataType == "Buff" and event.target in self.statDict:
            if event.id in self.CALLS:
                fresh = self.callBuff(event, *self.CALLS[event.id])
                if fresh and event.id in ("34113", "34114", "34115"):
                    self.increment(event.target, "shadowCalls", time=event.time)
                elif fresh and event.id == "34324":
                    self.increment(event.target, "wingCalls", time=event.time)
                elif fresh and event.id == "34543":
                    self.increment(event.target, "flyingCalls", time=event.time)
            if event.id == "34278":
                previous = self.fragmentStacks.get(event.target, 0)
                if event.stack > previous:
                    self.increment(event.target, "fragmentPickups", event.stack-previous, time=event.time)
                self.fragmentStacks[event.target] = event.stack
            if event.id == "34057":
                self.stunCounter[event.target].setState(event.time, event.stack > 0)
            elif event.id == "34619":
                self.invasionStacks.append((event.time, event.target, event.stack))
                stats = self.statDict[event.target]["battle"]
                stats["invasionMax"] = max(stats.get("invasionMax", 0), event.stack)
                if event.stack > 3 and event.target not in self.invasionFailure:
                    self.invasionFailure.add(event.target)
                    self.confirmedFailure(event.target, event.time, "煞气侵袭超过3层",
                                           "34619气劲超过3层；解包描述为只能抵挡三次煞气爆发。")
                elif event.stack == 0:
                    self.invasionFailure.discard(event.target)
        elif event.dataType == "Shout":
            if self.template(event.id) in self.MAIN_IDS:
                content = event.content.strip('"')
                if content in self.SHOUTS:
                    record_shout(self, event, self.SHOUTS[content])
                if content == self.TRANSITION_START and self.phase == 1:
                    self.changePhase(event.time, 2)
                    self.detail["phaseChanges"].append({"time": event.time, "phase": 2,
                        "source": "本体煞甲归身喊话"})
                    self.bh.setEnvironment("0", "本体红黑煞阶段", "16371", event.time,
                        0, 1, "本体煞甲归身喊话", "phase", "#9944bb")
                    self.transitionStart = event.time
                elif content == self.TRANSITION_END and self.transitionStart is not None:
                    self.finishTransition(event.time, False)
            elif self.template(event.id) in self.LIFU_IDS:
                content = event.content.strip('"')
                if content in self.LIFU_SHOUTS:
                    record_shout(self, event, self.LIFU_SHOUTS[content])
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
                if event.enter and event.id not in self.shaStart:
                    self.shaStart[event.id] = event.time
                    self.bh.setEnvironment(template, "煞将", "16371", event.time, 0, 1, "煞将入场", "npc", "#cc8800")
                    tag_source(self, event.id)
                elif not event.enter:
                    self.finishSha(event.id, event.time)
        elif event.dataType == "Death":
            if self.template(event.id) in self.MAIN_IDS and self.lastMainDamage is not None:
                self.confirmWin(event.time, "main_npc_death")
            self.finishSha(event.id, event.time)
        super().analyseSecondStage(event)

    def finishTransition(self, time, truncated):
        if self.transitionStart is None:
            return
        start = self.transitionStart
        self.detail["transitionPeriods"].append({"start": start, "end": max(start, time),
            "name": "煞甲归身转场（喊话观测）", "duration": round(max(0, time-start)/1000, 3),
            "truncated": truncated})
        self.bh.setEnvironment("0", "煞甲归身转场（喊话观测）", "16371", start,
            max(0, time-start), 1, "双本体喊话边界；无目标输出区间另据对象退场和有效伤害核验，治疗有效", "transition", "#9944bb")
        self.transitionStart = None

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
        self.finishTransition(end, True)
        for period in self.detail["transitionPeriods"]:
            evidence = self.transitionAvailability.resolve(
                period['start'], period['end'], end, not period['truncated'])
            period['dpsExclusion'] = evidence
            if evidence['affectDps']:
                self.bh.setBadPeriod(evidence['start'], evidence['end'], True, False)
        for npc_id in list(self.shaStart):
            self.finishSha(npc_id, end)
        self.finishEncounter()
        for stats in self.statDict.values():
            stats["battle"]["invasionMax"] = 0
        for time, player, stack in self.invasionStacks:
            if time <= end:
                stats = self.statDict[player]["battle"]
                stats["invasionMax"] = max(stats["invasionMax"], stack)
        super().countFinal()
        finalize_phase_periods(self, {1: "煞将/剑符", 2: "本体红黑煞", 3: "三阶段"}, "phaseChanges")
        for phase in range(1, 4):
            self.detail["P%dTime" % phase] = round(self.phaseTime[phase]/1000, 2)
        self.detail["phaseTimes"] = {"煞将/剑符": self.detail["P1Time"], "本体红黑煞": self.detail["P2Time"], "三阶段": self.detail["P3Time"]}
        self.detail["phaseSummary"] = "煞将/剑符 %.1f秒 / 本体红黑煞 %.1f秒 / 三阶段 %.1f秒（喊话优先/招式回退）" % (
            self.detail["P1Time"], self.detail["P2Time"], self.detail["P3Time"])
