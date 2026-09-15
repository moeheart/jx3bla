"""伊曼双子：双本体、火环区段、点名/眩晕与下一首领串入裁剪。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, finalize_evidence, render_boss_window,
)


class YimanTwinsWindow(SpecificBossWindow):
    def loadWindow(self):
        render_boss_window(self, "伊曼双子", [
            ("nightDamageDps", "寂夜DPS", "仅伊曼·寂夜本体有效伤害/有效时间。"),
            ("fireDamageDps", "逐焰DPS", "仅伊曼·逐焰本体有效伤害/有效时间。"),
            ("lockCalls", "逐焰锁定", "34597气劲的独立锁定次数。"),
            ("chainHits", "横扫命中", "锁链横扫直接伤害命中；眩晕气劲单独记入个人控制时间。"),
            ("ringHits", "火环命中", "链舞火环命中，观察记录。"),
            ("inertDamageDps", "机关伤害", "不可选择的不死机关139320/139718伤害单列，不混入双本体。"),
        ])


class YimanTwinsReplayer(GeneralReplayer):
    NIGHT = ("139319",)
    FIRE = ("139322",)
    MAIN = NIGHT + FIRE
    SOURCES = MAIN + ("139327", "139320", "139718")
    ENVIRONMENT = {
        ("Skill", "45909"): ("逐猎爆弹", "12453", "#dd7733"),
        ("Skill", "45910"): ("散雷延爆", "340", "#ddaa33"),
        ("Skill", "45899"): ("锁链横扫", "2123", "#7755aa"),
        ("Skill", "45911"): ("爆裂轰退", "340", "#cc6633"),
        ("Skill", "45897"): ("链坠天崩", "2123", "#5555aa"),
        ("Cast", "45912"): ("链舞火环", "12452", "#dd5533"),
        ("Skill", "45908"): ("焚天炽焰", "12452", "#cc3333"),
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "伊曼双子"
        self.initPhase(2, 1)
        self.activeRings = set()
        self.deadBosses = set()
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "双子交战"}]
        self.detail["limitations"] = "阶段仅标注日志可见火环区间；不能从单只首领退场、血量阈值或文件顺序推断双子通关。"
        for npc_id in self.bld.info.npc:
            if npc_matches(self, npc_id, self.MAIN):
                self.bh.setMainTarget(npc_id)

    def analyseSecondStage(self, event):
        if event.dataType == "Shout" and npc_matches(self, event.id, ("139327",)):
            if event.content.strip('"') == "一切都结束了":
                set_confirmed_win(self, event.time, "双子场控结束喊话")
        elif event.dataType in ("Scene", "Death"):
            if npc_matches(self, event.id, ("140056",)) and (event.dataType == "Death" or event.enter):
                set_confirmed_win(self, event.time, "伊曼专属宝箱")
            elif event.dataType == "Death" and npc_matches(self, event.id, self.MAIN):
                self.deadBosses.add(str(self.bld.info.npc[event.id].templateID))
                if set(self.MAIN).issubset(self.deadBosses):
                    set_confirmed_win(self, event.time, "双本体重伤")
        if self.win and event.time > self.winTime:
            return
        if event.dataType == "Scene" and npc_matches(self, event.id, ("139718",)):
            if event.enter:
                self.activeRings.add(event.id)
                record_phase(self, event.time, 2, "链舞火环")
            else:
                self.activeRings.discard(event.id)
                if not self.activeRings:
                    record_phase(self, event.time, 1, "双子交战")
        elif event.dataType == "Skill":
            if npc_matches(self, event.target, self.NIGHT):
                record_target_damage(self, event, "nightDamage")
            elif npc_matches(self, event.target, self.FIRE):
                record_target_damage(self, event, "fireDamage")
            elif npc_matches(self, event.target, ("139320", "139718")):
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
                if record_call_buff(self, event, "逐焰锁定", "12453"):
                    self.statDict[event.target]["lockCalls"] = self.statDict[event.target].get("lockCalls", 0) + 1
            elif event.id == "34504" and event.target in self.stunCounter:
                record_call_buff(self, event, "锁链横扫·眩晕", "2123")
                self.stunCounter[event.target].setState(event.time, int(event.stack > 0))

    def countFinal(self):
        super().countFinal()
        finalize_evidence(self, {1: "双子交战", 2: "链舞火环"},
                          ("nightDamage", "fireDamage", "inertDamage"))
