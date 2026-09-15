"""洛阳之战阿史那承庆：玄隼、邪渊、聚邪循环（与阆风悬城独立）。"""
from replayer.boss.luoyangzhizhan.EncounterSupport import EncounterReplayer, EncounterWindow


class LuoyangAshinaChengqingWindow(EncounterWindow):
    TITLE = "洛阳之战·阿史那承庆"
    COLUMNS = (
        ("mainDps", "本体DPS", "只统计洛阳之战阿史那承庆本体，分母为裁剪后的战斗时间。"),
        ("constructDamage", "金刚伤害", "对玄隼、炽虎、伏焰金刚的有效伤害总量。"),
        ("bombCalls", "投弹点名", "投弹目标气劲的新获得次数，不累计刷新。"),
        ("soulCalls", "聚邪点名", "聚邪气劲的新获得次数。"),
        ("bombHits", "弹爆受击", "玄隼弹爆命中次数，同秒命中合并。只记录受击，不直接判责。"),
        ("abyssMax", "失魂最高层", "失魂气劲最高层数；5层的即死机制有解包描述依据。"),
    )


class LuoyangAshinaChengqingReplayer(EncounterReplayer):
    BOSS = "阿史那承庆"
    MAIN_IDS = ("139323", "139378", "138376")
    # Other construct template IDs are deliberately matched by their exact names below.
    CONSTRUCT_NAMES = ("玄隼金刚", "炽虎金刚", "伏焰金刚")
    CHEST_IDS = tuple(str(x) for x in range(140057, 140063)) + tuple(str(x) for x in range(140098, 140104))
    CALLS = {
        "34208": ("凝渊", "3399"), "34251": ("聚邪", "4492"),
        "34256": ("投弹目标", "25109"), "34258": ("携带玄隼弹", "14157"),
        "34394": ("伏焰锁定", "341"), "34357": ("爆裂残魂", "4528"),
    }
    CASTS = {
        "45566": "染魂", "46491": "凝渊刀", "45556": "邪魂散",
        "45883": "黄泉斩", "45916": "聚邪凝渊", "45937": "召唤玄隼",
        "46467": "召唤炽虎", "46293": "铁颚扑咬",
    }

    def initBattle(self):
        super().initBattle()
        self.initPhase(2, 1)
        self.soulStart = None
        self.soulHolders = set()
        self.soulResolved = False
        self.soulImmunity = {}
        self.abyssFailures = set()
        self.constructStart = {}
        self.detail["soulPeriods"] = []
        self.detail["constructPeriods"] = []
        self.detail["phaseEvidence"] = "常规与聚邪循环；聚邪从45916读条到本轮聚邪点名全部结束。"
        self.detail["mechanicNote"] = "玄隼弹爆、邪魂散、黄泉斩仅记录受击；失魂达到5层、已有邪魂入体再中聚邪才记录机制失败。常规与聚邪均计有效时间。"
        self.bhBlackList.extend(["s34061", "s34259", "s46376", "b34061", "b34259"])
        self.bhBlackList.extend("c"+x for x in self.CASTS)
        self.bhBlackList.extend("b"+x for x in self.CALLS)

    def finishSoul(self, time):
        if self.soulStart is None:
            return
        self.detail["soulPeriods"].append({"start": self.soulStart, "end": time})
        self.changePhase(time, 1)
        self.soulStart = None
        self.soulHolders.clear()

    def analyseSecondStage(self, event):
        if self.confirmedEnd is not None and event.time > self.confirmedEnd:
            return
        if event.dataType == "Skill":
            self.recordDamage(event, self.MAIN_IDS, "mainDamage")
            if (event.caster in self.statDict and event.target in self.bld.info.npc
                    and self.bld.info.getName(event.target) in self.CONSTRUCT_NAMES and event.damageEff > 0):
                self.recordContribution(event, "constructDamage")
            if event.caster in self.bld.info.npc:
                if event.id == "45954":
                    self.observedHit(event, "bombHits", "玄隼弹爆")
                elif event.id in ("45557", "45558", "45559", "45560"):
                    self.observedHit(event, "evilSoulHits", "邪魂散")
                elif event.id == "45884":
                    self.observedHit(event, "slashHits", "黄泉斩")
                elif event.id == "45932" and event.target in self.statDict:
                    active = self.soulImmunity.get(event.target)
                    if active is not None and event.time-active > 100 and self.observedHit(event, "repeatSoul", "重复承受聚邪"):
                        self.confirmedFailure(event.target, event.time, "邪魂入体期间再次承受聚邪",
                                              "34252气劲仍在，随后受到45932聚邪伤害。")
        elif event.dataType == "Buff" and event.target in self.statDict:
            if event.id in self.CALLS:
                fresh = self.callBuff(event, *self.CALLS[event.id])
                if fresh and event.id in ("34256", "34251"):
                    self.increment(event.target, "bombCalls" if event.id == "34256" else "soulCalls")
                if event.id == "34251":
                    if event.stack > 0:
                        self.soulHolders.add(event.target)
                        self.soulResolved = True
                    else:
                        self.soulHolders.discard(event.target)
                        if self.soulResolved and not self.soulHolders:
                            self.finishSoul(event.time)
            elif event.id == "34252":
                if event.stack > 0:
                    self.soulImmunity.setdefault(event.target, event.time)
                else:
                    self.soulImmunity.pop(event.target, None)
            elif event.id == "34226":
                self.stunCounter[event.target].setState(event.time, event.stack > 0)
            elif event.id == "34376":
                stats = self.statDict[event.target]["battle"]
                stats["abyssMax"] = max(stats.get("abyssMax", 0), event.stack)
                if event.stack >= 5 and event.target not in self.abyssFailures:
                    self.abyssFailures.add(event.target)
                    self.confirmedFailure(event.target, event.time, "失魂达到5层", "34376失魂气劲达到5层；解包描述为即死且无法复活。")
                if event.stack == 0:
                    self.abyssFailures.discard(event.target)
        elif event.dataType == "Cast" and self.template(event.caster) in self.MAIN_IDS:
            if event.id in self.CASTS:
                self.bh.setEnvironment(event.id, self.CASTS[event.id], "3399", event.time, 0, 1, "首领运功", "cast", "#9944bb")
            if event.id == "45916":
                self.finishSoul(event.time)
                self.soulStart = event.time
                self.soulResolved = False
                self.changePhase(event.time, 2)
        elif event.dataType == "Scene":
            name = self.bld.info.getName(event.id)
            if event.enter and self.template(event.id) in self.CHEST_IDS and self.lastMainDamage is not None:
                self.confirmWin(event.time, "boss_chest")
            if name in self.CONSTRUCT_NAMES:
                if event.enter and event.id not in self.constructStart:
                    self.constructStart[event.id] = (event.time, name)
                    self.bh.setEnvironment(self.template(event.id), name, "14157", event.time, 0, 1, "金刚入场", "npc", "#cc8800")
                elif not event.enter:
                    self.finishConstruct(event.id, event.time)
        elif event.dataType == "Death":
            if self.template(event.id) in self.MAIN_IDS and self.lastMainDamage is not None:
                self.confirmWin(event.time, "main_npc_death")
            self.finishConstruct(event.id, event.time)
        super().analyseSecondStage(event)

    def finishConstruct(self, npc_id, time):
        if npc_id in self.constructStart:
            start, name = self.constructStart.pop(npc_id)
            self.detail["constructPeriods"].append({"start": start, "end": time, "name": name})

    def countFinal(self):
        if self.finalized:
            return
        self.finalized = True
        end = self.encounterEnd()
        self.finishSoul(end)
        for npc_id in list(self.constructStart):
            self.finishConstruct(npc_id, end)
        self.finishEncounter()
        super().countFinal()
        self.detail["P1Time"] = round(self.phaseTime[1]/1000, 2)
        self.detail["P2Time"] = round(self.phaseTime[2]/1000, 2)
        self.detail["phaseTimes"] = {"常规": self.detail["P1Time"], "聚邪": self.detail["P2Time"]}
        self.detail["phaseSummary"] = "常规 %.1f秒 / 聚邪 %.1f秒；金刚出现 %d 次" % (
            self.detail["P1Time"], self.detail["P2Time"], len(self.detail["constructPeriods"]))


# Explicit aliases are convenient for map-specific imports; the old module is untouched.
AshinaChengqingReplayer = LuoyangAshinaChengqingReplayer
AshinaChengqingWindow = LuoyangAshinaChengqingWindow
