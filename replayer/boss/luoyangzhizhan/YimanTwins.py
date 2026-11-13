"""伊曼双子：双本体、火环区段、点名/眩晕与下一首领串入裁剪。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_reflected_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, record_shout, finalize_evidence, render_boss_window,
)


class YimanTwinsWindow(SpecificBossWindow):
    def loadWindow(self):
        columns = [
            ("nightDamageDps", "寂夜DPS", "仅伊曼·寂夜本体有效伤害/有效时间。"),
            ("fireDamageDps", "逐焰DPS", "仅伊曼·逐焰本体有效伤害/有效时间。"),
            ("lockCalls", "逐焰锁定", "34597气劲的独立锁定次数。"),
            ("chainHits", "横扫命中", "锁链横扫直接伤害命中；眩晕气劲单独记入个人控制时间。"),
            ("ringHits", "火环命中", "链舞火环命中，观察记录。"),
            ("inertDamageDps", "机关伤害", "不可选择的不死机关及火环伤害单列，不混入双本体或可击破锁链。"),
        ]
        if self.detail.get("heroic"):
            columns[2:2] = [
                ("chainDamageDps", "锁链DPS", "英雄可攻击锁链139716有效伤害/有效时间；不混入双本体或不死机关。"),
                ("prisonCalls", "钉柱点名", "钉柱炼狱34270的独立气劲区间，持续刷新不重复计数；控制时间与横扫眩晕取并集。"),
            ]
        render_boss_window(self, "伊曼双子", columns)


class YimanTwinsReplayer(GeneralReplayer):
    NIGHT = ("139319", "139373")
    FIRE = ("139322", "139376")
    MAIN = NIGHT + FIRE
    CHAINS = ("139716",)
    RINGS = ("139718", "139717")
    INERT = ("139320", "139374") + RINGS
    SOURCES = MAIN + INERT + CHAINS + ("139327", "139372")
    ENVIRONMENT = {
        ("Skill", "45909"): ("逐猎爆弹", "12453", "#dd7733"),
        ("Skill", "45910"): ("散雷延爆", "340", "#ddaa33"),
        ("Skill", "45899"): ("锁链横扫", "2123", "#7755aa"),
        ("Skill", "45911"): ("爆裂轰退", "340", "#cc6633"),
        ("Skill", "45897"): ("链坠天崩", "2123", "#5555aa"),
        # A fresh ring NPC casts every2.5s in the same observed ring phase.
        # Keep one fallback per wave when Scene evidence is absent.
        ("Cast", "45912"): ("链舞火环", "12452", "#dd5533", {"burstGap": 7500, "perSource": False, "heroicOnly": True}),
        ("Skill", "45908"): ("焚天炽焰", "12452", "#cc3333"),
        ("Skill", "45906"): ("钉柱链狱", "2123", "#7755aa", {"burstGap": 6000, "heroicOnly": True}),
    }

    NIGHT_SHOUTS = {
        "天锁垂落，罪冤退散！": "链坠天崩",
        "鞭打众生，哀鸣荡尽！": "锁链横扫",
        "妹妹！让无尽的圣火，熊熊燃烧吧！": "链舞火环准备",
        "链为牢，柱为枷——送魂！": "钉柱炼狱准备",
        "挣扎吧，挣扎会让神灵更加愉悦……圣恩降临！": "钉柱链狱",
        "祭品已纳，圣恩已成！": "圣恩已成",
    }
    FIRE_SHOUTS = {
        "跑啊！跑快点！": "逐焰追击",
        "抬头，接火！": "逐猎爆弹",
        "早就迫不及待了！": "圣火回应",
        "姐姐！！—炸碎你们,统统炸碎！！！": "逐焰独战",
        "竟敢伤我们到这种程度。黑暗，定会吞噬你们！": "双子战败",
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "伊曼双子"
        self.detail["heroic"] = any(npc_matches(self, npc_id, ("139373", "139376")) for npc_id in self.bld.info.npc)
        self.initPhase(4, 1)
        self.lastMainDamage = None
        self.activeRings = set()
        self.deadBosses = set()
        self.controlBuffs = {player: set() for player in self.statDict}
        self.chainRecords = {}
        self.detail["chains"] = []
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "双子交战"}]
        self.detail["limitations"] = "火环准备按寂夜喊话、火环实体按场景事件、逐焰独战按逐焰喊话划段；不从单体退场或血量阈值推断通关。"
        for npc_id in self.bld.info.npc:
            if npc_matches(self, npc_id, self.MAIN):
                self.bh.setMainTarget(npc_id)

    def analyseSecondStage(self, event):
        if event.dataType == "Shout" and npc_matches(self, event.id, ("139327",)):
            if event.content.strip('"') == "一切都结束了":
                set_confirmed_win(self, event.time, "双子场控结束喊话")
        elif event.dataType == "Shout" and npc_matches(self, event.id, self.MAIN):
            content = event.content.strip('"')
            mapping = self.NIGHT_SHOUTS if npc_matches(self, event.id, self.NIGHT) else self.FIRE_SHOUTS
            label = mapping.get(content)
            if label and not (self.win and event.time > self.winTime):
                record_shout(self, event, label)
                if label == "链舞火环准备" and self.phase != 4:
                    record_phase(self, event.time, 3, label)
                elif label == "逐焰独战":
                    record_phase(self, event.time, 4, label)
                elif label == "双子战败" and self.lastMainDamage is not None and 0 <= event.time - self.lastMainDamage <= 5000:
                    set_confirmed_win(self, event.time, "逐焰本体战败喊话及近期本体伤害")
        elif event.dataType in ("Scene", "Death"):
            if npc_matches(self, event.id, ("140056", "140097")) and (event.dataType == "Death" or event.enter):
                set_confirmed_win(self, event.time, "伊曼专属宝箱")
            elif event.dataType == "Death" and npc_matches(self, event.id, self.MAIN):
                self.deadBosses.add(str(self.bld.info.npc[event.id].templateID))
                if self.deadBosses.intersection(self.NIGHT) and self.deadBosses.intersection(self.FIRE):
                    set_confirmed_win(self, event.time, "双本体重伤")
        if self.win and event.time > self.winTime:
            return
        if event.dataType in ("Scene", "Death") and npc_matches(self, event.id, self.CHAINS):
            if event.dataType == "Scene" and event.enter:
                self.chainRecords[event.id] = {"start": event.time, "end": None, "killed": False}
            else:
                record = self.chainRecords.setdefault(event.id, {"start": self.startTime, "killed": False})
                if record.get("end") is None:
                    record["end"] = event.time
                if event.dataType == "Death":
                    record["killed"] = True
        elif event.dataType == "Scene" and npc_matches(self, event.id, self.RINGS):
            if event.enter:
                self.activeRings.add(event.id)
                if self.phase != 4:
                    record_phase(self, event.time, 2, "链舞火环")
            else:
                self.activeRings.discard(event.id)
                if not self.activeRings and self.phase == 2:
                    record_phase(self, event.time, 1, "双子交战")
        elif event.dataType == "Skill":
            record_reflected_target_damage(self, event, {
                "nightDamage": self.NIGHT, "fireDamage": self.FIRE,
                "chainDamage": self.CHAINS, "inertDamage": self.INERT,
            })
            if (npc_matches(self, event.target, self.MAIN) and
                    event.caster in self.statDict and event.damageEff > 0):
                self.lastMainDamage = event.time
            if npc_matches(self, event.target, self.NIGHT):
                record_target_damage(self, event, "nightDamage")
            elif npc_matches(self, event.target, self.FIRE):
                record_target_damage(self, event, "fireDamage")
            elif npc_matches(self, event.target, self.CHAINS):
                record_target_damage(self, event, "chainDamage")
            elif npc_matches(self, event.target, self.INERT):
                record_target_damage(self, event, "inertDamage")
            if npc_matches(self, event.caster, self.SOURCES):
                record_environment(self, event, self.ENVIRONMENT)
                hits = {"45899": ("chainHits", "锁链横扫"), "45912": ("ringHits", "链舞火环"),
                        "45908": ("flameHits", "焚天炽焰")}
                if event.id in hits:
                    record_hit(self, event, *hits[event.id])
        elif event.dataType == "Cast" and npc_matches(self, event.caster, self.SOURCES):
            record_environment(self, event, self.ENVIRONMENT)
        elif event.dataType == "Buff" and npc_matches(self, event.caster, self.SOURCES):
            if event.id == "34597":
                record_call_buff(self, event, "逐焰锁定", "12453", stat_key="lockCalls")
            elif event.id in ("34504", "34270") and event.target in self.stunCounter:
                label = "钉柱炼狱" if event.id == "34270" else "锁链横扫·眩晕"
                record_call_buff(self, event, label, "2123",
                                 stat_key="prisonCalls" if event.id == "34270" else None)
                active = self.controlBuffs[event.target]
                if event.stack > 0:
                    active.add(event.id)
                else:
                    active.discard(event.id)
                self.stunCounter[event.target].setState(event.time, int(bool(active)))

    def countFinal(self):
        if self.__dict__.get("_luoyangEvidenceFinalized"):
            return
        for npc_id, record in self.chainRecords.items():
            if record["start"] > self.finalTime:
                continue
            observed_end = record.get("end")
            end = min(observed_end or self.finalTime, self.finalTime)
            self.detail["chains"].append(dict(
                record, npcID=npc_id, end=end,
                killed=bool(record.get("killed") and observed_end is not None and observed_end <= self.finalTime),
                truncated=observed_end is None or observed_end > self.finalTime,
                duration=max(0, end-record["start"]) / 1000))
            self.bh.setEnvironment("139716", "锁链", "2123", record["start"],
                                   max(0, end-record["start"]), 1, "锁链实体在场区间；退场不单独判定击破", "npc", "#7755aa")
        super().countFinal()
        finalize_evidence(self, {1: "双子交战", 2: "链舞火环", 3: "链舞火环准备", 4: "逐焰独战"},
                          ("nightDamage", "fireDamage", "chainDamage", "inertDamage"))
