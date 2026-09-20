"""Regression coverage for extraction and replay table selection."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from data.DataContent import OverallData, SingleDataBuff
from equip.AttributeDisplay import AttributeDisplay
from replayer import Name, NameCangsheng
from replayer.CombatTracker import CombatTracker, getResistedAmounts
from release.NameGenerator import build_tables, parse_buff
from tools.Attribute import COEFF50


RESOURCE = Path(__file__).resolve().parents[1] / "equip/resources/cangshengtf"


def buff(*attributes):
    row = {"ID": "123", "Level": "3"}
    for index, (attribute, value) in enumerate(attributes, 1):
        row["BeginAttrib%d" % index] = attribute
        row["BeginValue%dA" % index] = str(value)
    return row


class BuffGenerationTests(unittest.TestCase):
    def test_multiple_attributes_levels_and_fraction(self):
        row = buff(("atTherapyPowerBase", 20), ("atTherapyPowerBase", 7),
                   ("atAllDamageAddPercent", "102.4"))
        row.update(ActiveAttrib1="atPhysicsAttackPowerBase", ActiveValue1A="999")
        _, boost, _, therapy = parse_buff(row)
        self.assertEqual(boost["atTherapyPowerBase"], 27)
        self.assertEqual(boost["atAllDamageAddPercent"], 102.4)
        self.assertNotIn("atPhysicsAttackPowerBase", boost)
        self.assertEqual(therapy["atTherapyPowerBase"], 27)

    def test_absorb_coefficient_and_therapy_absorb_are_not_damage_shields(self):
        self.assertFalse(parse_buff(buff(("atDamageAbsorbShieldCoefficient", 102)))[0])
        self.assertFalse(parse_buff(buff(("atGlobalTherapyAbsorb", 200)))[0])
        self.assertTrue(parse_buff(buff(("atGlobalDamageAbsorbBySelfMaxLife", 0)))[0])

    def test_single_school_is_not_global_and_invalid_numbers_fail(self):
        resistance = parse_buff(buff(("atLunarDamageCoefficient", -307)))[2]
        self.assertEqual(resistance, {"Lunar": 307})
        with self.assertRaises(ValueError):
            parse_buff(buff(("atAllDamageAddPercent", "bad")))
        self.assertFalse(parse_buff(buff(("atPhysicsDamageCoefficient", "")))[2])

    def test_full_regeneration_matches_committed_tables(self):
        for key, value in build_tables(RESOURCE).items():
            self.assertEqual(value, getattr(NameCangsheng, key), key)

    def test_current_source_and_verified_regressions(self):
        manifest = json.loads((RESOURCE / "source_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["client_version"], "1.6.0.9506")
        core_files = set(manifest["core_update"]["files"])
        self.assertEqual(len(core_files), 14)
        for source in manifest["files"]:
            self.assertEqual(hashlib.sha256((RESOURCE / source["name"]).read_bytes()).hexdigest(), source["sha256"])
            if source["name"] in core_files:
                self.assertEqual(source["client_version"], "1.6.0.9506")
                self.assertEqual(source["extraction_date"], "2026-09-20")
                self.assertIn("luoyangzhizhan-0920-check", source["source_path"])
            else:
                self.assertEqual(source["client_version"], "1.6.0.9503")
                self.assertFalse(source["reextracted_for_release_8_16_0"])
        # These same-name strain buffs must stay on their precise IDs/levels.
        for identifier in (29294, 20938, 23543):
            self.assertEqual(NameCangsheng.BOOST_DICT["2,%d,1" % identifier], {"atStrainBase": 7})
        self.assertEqual(NameCangsheng.BOOST_DICT["2,23107,1"]["atStrainBase"], 34)
        self.assertEqual(NameCangsheng.BOOST_DICT["2,2197,4"]["atAgilityBasePercentAdd"], 307)
        self.assertEqual(NameCangsheng.BOOST_DICT["2,22847,5"]["atPhysicsShieldBase"], 0)
        self.assertNotIn("2,9336,1", NameCangsheng.RESIST_DICT)
        self.assertEqual(NameCangsheng.RESIST_DICT["2,33086,30"], 307)
        self.assertEqual(NameCangsheng.RESIST_DICT["2,33086,15"], 154)
        self.assertIn("2,9337,2", NameCangsheng.THERAPY_DICT)
        self.assertAlmostEqual(COEFF50["会心"], 9.609 * 990)
        self.assertAlmostEqual(COEFF50["加速"], 10.21 * 990)


class ReplayProfileTests(unittest.TestCase):
    def tracker(self, map_name, players=False):
        info = OverallData()
        info.map, info.battleTime, info.skill = map_name, 1789470000, {}
        history = SimpleNamespace(badPeriodDpsLog=[], badPeriodHealerLog=[], critPeriodHealerLog=[],
                                  critPeriodSum=0, mainTargets=[], startTime=0, finalTime=10000)
        if players:
            info.player = {name: SimpleNamespace(name=name, occ="4p") for name in ("target", "a", "b", "shield")}
        return CombatTracker(info, history, {name: "4p" for name in info.player}, {}, {},
                             {name: {"id": "0", "stack": 0} for name in ("zxyz", "qs", "zzm")},
                             {name: None for name in info.player})

    def event(self, source="a", slot="1", stack=1, time=1000, level=15, id="33086", valid=None):
        item = ["0", "0", "0", str(time), "13", {"1": "target", "2": "false", "3": slot,
                "4": "true", "5": id, "6": str(stack), "7": "0", "9": str(level), "10": source}]
        result = SingleDataBuff()
        if valid is not None:
            item[5]["11"] = "true" if valid else "false"
        result.setByJcl(item)
        return result

    def test_versions_are_instance_local(self):
        new = self.tracker("25人普通洛阳之战")
        old = self.tracker("25人普通阆风悬城")
        self.assertIs(new.boostDict, NameCangsheng.BOOST_DICT)
        self.assertIs(old.boostDict, Name.BOOST_DICT)
        self.assertEqual(new.bosslvl, 53)
        self.assertEqual(old.bosslvl, 133)
        new.export(10000, 10000, 10000, {})
        old.export(10000, 10000, 10000, {})
        self.assertEqual(new.generateJson()["rdps"]["status"], "incomplete")
        self.assertEqual(old.generateJson()["rdpsStatus"]["status"], "supported")

    def test_school_reduction_and_unknown_absorbed_school(self):
        only_lunar = {"buff": ["player", 0, {"Lunar": 512}]}
        self.assertEqual(getResistedAmounts({"0": "100"}, only_lunar, 100), {})
        self.assertEqual(getResistedAmounts({"3": "100"}, only_lunar, 100), {"buff": 100})
        self.assertEqual(getResistedAmounts({}, only_lunar, 0, 100), {})
        uniform = {"buff": ["player", 0, {school: 512 for school in ("Physics", "Solar", "Lunar", "Neutral", "Poison")} ]}
        self.assertEqual(getResistedAmounts({}, uniform, 0, 100), {"buff": 100})

    def test_unknown_school_does_not_ignore_school_specific_effects(self):
        buffs = {"global": ["a", 0, {school: 256 for school in ("Physics", "Solar", "Neutral", "Lunar", "Poison")}],
                 "lunar": ["b", 0, {"Lunar": 256}]}
        self.assertEqual(getResistedAmounts({}, buffs, 0, 100), {})

    def test_signed_vulnerability_full_reduction_and_mixed_school_damage(self):
        buffs = {"reduce": ["a", 0, {"Physics": 512}], "vulnerable": ["b", 0, {"Physics": -256}]}
        self.assertEqual(getResistedAmounts({"0": "300"}, buffs, 300), {"reduce": 200})
        buffs["vulnerable"][2]["Physics"] = -768
        self.assertEqual(getResistedAmounts({"0": "500"}, buffs, 500), {"reduce": 200})
        buffs["vulnerable"][2]["Physics"] = 512
        self.assertEqual(getResistedAmounts({"0": "1"}, buffs, 1), {})
        mixed = {"physical": ["a", 0, {"Physics": 512}], "lunar": ["b", 0, {"Lunar": 256}]}
        self.assertEqual(getResistedAmounts({"0": "100", "3": "300"}, mixed, 400, 200),
                         {"physical": 100, "lunar": 100})

    def test_shared_reduction_preserves_slots_sources_and_removes_one(self):
        tracker = self.tracker("25人普通洛阳之战", players=True)
        tracker.shieldDict["target"] = "shield"
        tracker.recordBuff(self.event(source="a", slot="11"))
        tracker.recordBuff(self.event(source="b", slot="12"))
        tracker.recordBuff(self.event(source="a", slot="13"))
        records = tracker.resistBuff["target"]
        self.assertEqual(len(records), 3)
        self.assertEqual([record[0] for record in records.values()], ["a", "b", "a"])
        self.assertTrue(all(record[3] == "2,33086,15" for record in records.values()))
        tracker.recordBuff(self.event(source="a", slot="11", stack=0, time=1100))
        tracker.checkRemoveBuff(1149)
        self.assertEqual(len(records), 3)
        tracker.checkRemoveBuff(1150)
        self.assertEqual(len(records), 2)
        self.assertNotIn(("2,33086,15", "slot", "11"), records)
        self.assertIn(("2,33086,15", "slot", "12"), records)
        # A refresh cancels only that slot's delayed removal.
        tracker.recordBuff(self.event(source="b", slot="12", stack=0, time=1200))
        tracker.recordBuff(self.event(source="b", slot="12", time=1220))
        tracker.checkRemoveBuff(1250)
        self.assertEqual(len(records), 2)
        tracker.recordSkill(SimpleNamespace(id="999", level=1, scheme=1, full_id="1,999,1", caster="a",
                            target="target", time=1300, damage=100, damageEff=100, heal=0, healEff=0,
                            effect=0, fullResult={"0": "100"}))
        self.assertIn("2,2,33086,15", tracker.ahpsCast["a"].skill)
        self.assertIn("2,2,33086,15", tracker.ahpsCast["b"].skill)
        self.assertEqual(tracker.ahpsCast["shield"].skill, {})
        self.assertIsInstance(tracker.ahpsCast["a"].getSkillName("2,2,33086,15", tracker.info), str)

    def test_new_unknown_level_does_not_use_zero_level_numeric_effect(self):
        new = self.tracker("25人普通洛阳之战", players=True)
        old = self.tracker("25人普通阆风悬城", players=True)
        new.resistDict = {"2,33086,0": {"Physics": 102}}
        old.resistDict = {"2,33086,0": 102}
        new.recordBuff(self.event(level=999))
        old.recordBuff(self.event(level=999))
        self.assertEqual(new.resistBuff["target"], {})
        self.assertIn("2,33086,999", old.resistBuff["target"])

    def test_qiusu_removing_old_slot_preserves_new_live_instance(self):
        tracker = self.tracker("25人普通洛阳之战", players=True)
        tracker.recordBuff(self.event(source='a', slot='81635', id='29294', level=1, stack=81, valid=True))
        counter = tracker.boostCounter['target']
        # The actual clear deletes another slot while 81635 is still active.
        tracker.recordBuff(self.event(source='a', slot='81771', id='29294', level=1, stack=0, time=1100))
        key = ('2,29294,1', 'slot', '81635')
        self.assertEqual(counter.boost[key]['effect']['atStrainBase'], 567)
        tracker.recordBuff(self.event(source='a', slot='81635', id='29294', level=1, stack=81, valid=False, time=1200))
        self.assertEqual(counter.boost, {})
        tracker.recordBuff(self.event(source='a', slot='81635', id='29294', level=1, stack=81, valid=True, time=1300))
        self.assertIn(key, counter.boost)

    def test_boost_expiry_and_refresh_use_log_end_frame(self):
        tracker = self.tracker('25人普通洛阳之战', players=True)
        buff = self.event(id='29294', level=1, stack=81)
        buff.frame, buff.end = 100, 116  # One second remaining at t=1000.
        tracker.recordBuff(buff)
        counter = tracker.boostCounter['target']
        tracker.checkRemoveBuff(1999)
        self.assertTrue(counter.boost)
        buff.time, buff.frame, buff.end = 1900, 114, 146
        tracker.recordBuff(buff)  # Refreshed expiry is t=3900, not t=2000.
        tracker.checkRemoveBuff(2000)
        self.assertTrue(counter.boost)
        tracker.checkRemoveBuff(3900)
        self.assertFalse(counter.boost)

    def test_other_zyhr_cast_cannot_replace_existing_buff_provider(self):
        tracker = self.tracker('25人普通洛阳之战', players=True)
        tracker.recordBuff(self.event(source='a', id='20854', level=1, stack=84))
        cast = SimpleNamespace(id='27674', level=1, scheme=1, full_id='1,27674,1', caster='b',
            target='target', time=1100, damage=0, damageEff=0, heal=0, healEff=0, effect=0, fullResult={})
        tracker.recordSkill(cast)
        self.assertEqual(tracker.boostCounter['target'].zyhr, 'a')
        tracker.recordBuff(self.event(source='b', slot='2', id='20854', level=1, stack=84, time=1200))
        self.assertEqual(tracker.boostCounter['target'].zyhr, 'b')

    def test_first_zyhr_proc_uses_cast_until_buff_record_arrives(self):
        tracker = self.tracker('25人普通洛阳之战', players=True)
        cast = SimpleNamespace(id='27674', level=1, scheme=1, full_id='1,27674,1', caster='b',
            target='target', time=1100, damage=0, damageEff=0, heal=0, healEff=0, effect=0, fullResult={})
        tracker.recordSkill(cast)
        self.assertEqual(tracker.boostCounter['target'].zyhr, 'b')
        tracker.recordBuff(self.event(source='a', id='20854', level=1, stack=84, time=1200))
        self.assertEqual(tracker.boostCounter['target'].zyhr, 'a')

    def test_nonzero_stack_invalid_instance_stops_immediately_and_can_reactivate(self):
        tracker = self.tracker("25人普通洛阳之战", players=True)
        tracker.recordBuff(self.event(slot="248", valid=True))
        tracker.recordBuff(self.event(slot="249", source="b", valid=True))
        invalid = self.event(slot="248", valid=False, time=1100)
        self.assertEqual(invalid.stack, 1)
        tracker.recordBuff(invalid)
        records = tracker.resistBuff["target"]
        self.assertEqual(list(records), [("2,33086,15", "slot", "249")])
        tracker.recordBuff(self.event(slot="248", valid=True, time=1200))
        self.assertEqual(len(records), 2)
        self.assertEqual(records[("2,33086,15", "slot", "248")][0], "a")
        old = self.tracker("25人普通阆风悬城", players=True)
        old.resistDict = {"2,33086,15": 154}
        old.recordBuff(invalid)
        self.assertIn("2,33086,15", old.resistBuff["target"])

    def test_shield_instance_validity_preserves_other_source_and_canonical_name(self):
        tracker = self.tracker("25人普通洛阳之战", players=True)
        tracker.recordBuff(self.event(id="9334", level=1, slot="11", valid=True))
        tracker.recordBuff(self.event(id="9334", level=1, slot="12", source="b", valid=True))
        tracker.recordBuff(self.event(id="9334", level=1, slot="11", valid=False, time=1100))
        self.assertEqual(list(tracker.absorbBuff["target"]), [("2,9334,1", "slot", "12")])
        tracker.recordSkill(SimpleNamespace(id="999", level=1, scheme=1, full_id="1,999,1", caster="a",
                            target="target", time=1200, damage=0, damageEff=0, heal=0, healEff=0,
                            effect=0, fullResult={"9": "100"}))
        self.assertIn("1,2,9334,1", tracker.ahpsCast["b"].skill)
        self.assertEqual(tracker.ahpsCast["a"].skill, {})

    def test_new_equipment_does_not_make_up_a_panel(self):
        display = AttributeDisplay(gameEdition=160)
        self.assertEqual(display.status["status"], "supported")
        self.assertIsNone(display.GetBaseAttrib("", "22h"))
        self.assertIsNone(display.GetPanelAttrib("", "22h"))
        self.assertIsNone(display.Display("", "22h"))
        self.assertEqual(display.ac.CalculateAll(""), {})
        self.assertEqual(display.GetRawEquipmentFeature("7,112206")["atPhysicsShieldBase"], 29)
        with self.assertRaises(KeyError):
            display.GetRawEquipmentFeature("7,999999999")


if __name__ == "__main__":
    unittest.main()
