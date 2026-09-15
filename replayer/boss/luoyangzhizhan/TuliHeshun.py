"""突利和顺：2026-09-15 普通体服三份 JCL 与当前解包表。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, finalize_evidence, render_boss_window,
)


class TuliHeshunWindow(SpecificBossWindow):
    def loadWindow(self):
        render_boss_window(self, "突利和顺", [
            ("bossDamageDps", "本体DPS", "仅模板139306本体有效伤害，除以有效战斗秒数；排除同名机制NPC。"),
            ("stingCalls", "潜渊点名", "潜渊之刺34238的独立点名次数。"),
            ("inkCalls", "倒悬点名", "倒悬之墨34210的独立点名次数。"),
            ("surgeHits", "奔涌命中", "玄溟奔涌实际命中次数；不自动判责。"),
            ("fireHits", "业火命中", "玄溟之火实际命中次数；不自动判责。"),
        ])


class TuliHeshunReplayer(GeneralReplayer):
    MAIN = ("139306",)
    SOURCES = ("139306", "139325", "139352", "139357", "139358", "139359", "139138", "139321")
    ENVIRONMENT = {
        ("Cast", "45485"): ("潜渊之刺", "12452", "#9357ce"),
        ("Cast", "45486"): ("倒悬之墨", "12453", "#555599"),
        ("Cast", "45487"): ("玄溟奔涌", "12449", "#3377cc"),
        ("Cast", "45488"): ("浊浪登天", "340", "#3399aa"),
        ("Cast", "45489"): ("死水微澜", "340", "#aa3377"),
        ("Skill", "46024"): ("玄溟之火", "12452", "#cc5533"),
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "突利和顺"
        self.initPhase(2, 1)
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "常规技能"}]
        self.detail["evidenceVersion"] = "苍生铸世体服 1.6.0.9503 / 2026-09-15"
        self.detail["limitations"] = "仅观测机制点名与实际命中；坍缩力场只有减速证据，不扣除全团输出时间。"
        for npc_id in self.bld.info.npc:
            if npc_matches(self, npc_id, self.MAIN):
                self.bh.setMainTarget(npc_id)

    def analyseSecondStage(self, event):
        if event.dataType in ("Scene", "Death"):
            if npc_matches(self, event.id, ("140044",)) and (event.dataType == "Death" or event.enter):
                set_confirmed_win(self, event.time, "突利和顺专属宝箱")
            elif event.dataType == "Death" and npc_matches(self, event.id, self.MAIN):
                set_confirmed_win(self, event.time, "突利和顺本体重伤")
        if self.win and event.time > self.winTime:
            return
        if event.dataType == "Skill":
            if npc_matches(self, event.target, self.MAIN):
                record_target_damage(self, event, "bossDamage")
            if npc_matches(self, event.caster, self.SOURCES):
                record_environment(self, event, self.ENVIRONMENT)
                hits = {"45493": ("surgeHits", "玄溟奔涌"), "46024": ("fireHits", "玄溟之火")}
                if event.id in hits:
                    record_hit(self, event, *hits[event.id])
        elif event.dataType == "Cast" and npc_matches(self, event.caster, self.SOURCES):
            record_environment(self, event, self.ENVIRONMENT)
            if event.id == "45489":
                record_phase(self, event.time, 2, "死水微澜")
        elif event.dataType == "Buff" and npc_matches(self, event.caster, self.MAIN):
            calls = {"34238": ("潜渊之刺", "12452", "stingCalls"),
                     "34210": ("倒悬之墨", "12453", "inkCalls"),
                     "34490": ("坍缩力场", "340", "fieldCalls")}
            if event.id in calls:
                label, icon, key = calls[event.id]
                if record_call_buff(self, event, label, icon):
                    self.statDict[event.target][key] = self.statDict[event.target].get(key, 0) + 1
            elif event.id == "33755" and event.stack > 0 and self.phase == 2:
                # The shared skill-resume marker is observed after 死水微澜.
                record_phase(self, event.time, 1, "常规技能")

    def countFinal(self):
        super().countFinal()
        finalize_evidence(self, {1: "常规技能", 2: "死水微澜"}, ("bossDamage",))
