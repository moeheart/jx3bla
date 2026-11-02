"""突利和顺：普通体服与 2026-11-02 正式服日志校准。"""
from replayer.boss.General import GeneralReplayer
from window.SpecificBossWindow import SpecificBossWindow
from replayer.boss.luoyangzhizhan.LuoyangEvidence import (
    npc_matches, record_target_damage, record_call_buff, set_confirmed_win,
    record_environment, record_hit, record_phase, record_shout, finalize_evidence, render_boss_window,
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

    SHOUTS = {
        "血祭筹备完毕，尔等一众，正好来做祭品！": "开战",
        "一刺封途，二刺索命，三刺诛绝！": "潜渊之刺",
        "别躲了，玄溟的目光，早已阻绝尔等去路。": "倒悬之墨",
        "血光为引，玄溟为杀，四海无门！": "玄溟奔涌",
        "玄溟作薪，烈焰为牢，此地即为尔等葬身之所！": "玄溟之火",
        "仪式已成，尔等，皆为祭品！": "浊浪登天",
    }

    def initBattle(self):
        super().initBattle()
        self.activeBoss = "突利和顺"
        self.initPhase(4, 1)
        self.activeFields = set()
        self.detail["phaseTransitions"] = [{"time": self.startTime, "phase": 1, "name": "常规技能"}]
        self.detail["evidenceVersion"] = "体服 2026-09-15 / 正式服 2026-11-02"
        self.detail["limitations"] = "按本体喊话、运功及坍缩力场实际消失划段；不从伤害空窗推断全团不可输出时间。"
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
        if event.dataType == "Shout" and npc_matches(self, event.id, self.MAIN):
            label = self.SHOUTS.get(event.content.strip('"'))
            if label:
                record_shout(self, event, label)
                if label == "玄溟之火":
                    record_phase(self, event.time, 4, label)
                elif label == "浊浪登天":
                    record_phase(self, event.time, 3, label)
        elif event.dataType == "Skill":
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
            elif event.id == "45488":
                record_phase(self, event.time, 3, "浊浪登天")
            elif event.id in ("45485", "45486", "45487"):
                record_phase(self, event.time, 1, "常规技能")
        elif event.dataType == "Buff" and npc_matches(self, event.caster, self.MAIN):
            calls = {"34238": ("潜渊之刺", "12452", "stingCalls"),
                     "34210": ("倒悬之墨", "12453", "inkCalls"),
                     "34490": ("坍缩力场", "340", "fieldCalls")}
            if event.id in calls:
                label, icon, key = calls[event.id]
                if record_call_buff(self, event, label, icon):
                    self.statDict[event.target][key] = self.statDict[event.target].get(key, 0) + 1
                if event.id == "34490" and event.target in self.statDict:
                    if event.stack > 0:
                        self.activeFields.add(event.target)
                    elif event.target in self.activeFields:
                        self.activeFields.remove(event.target)
                        if not self.activeFields and self.phase == 2:
                            record_phase(self, event.time, 1, "常规技能")
            elif event.id == "33755" and event.stack > 0 and self.phase == 2:
                # The shared skill-resume marker is observed after 死水微澜.
                record_phase(self, event.time, 1, "常规技能")

    def countFinal(self):
        super().countFinal()
        finalize_evidence(self, {1: "常规技能", 2: "死水微澜", 3: "浊浪登天", 4: "玄溟之火"}, ("bossDamage",))
