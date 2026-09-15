"""Regression checks for target-specific level-50 rDPS defense coefficients."""
import copy
import json
import unittest
from pathlib import Path

from replayer.CombatTracker import getDamageCoeff


SCHOOLS = ("Physics", "Solar", "Lunar", "Neutral", "Poison")
ROOT = Path(__file__).resolve().parents[1]


class DamageCoeffTests(unittest.TestCase):
    def setUp(self):
        self.attrib = {"类型": 1, "攻击": 1000, "会心": 0, "会心效果": 1.75}
        self.profile = {"level": 53, "shieldBase": dict.fromkeys(SCHOOLS, 6399)}

    def coeff(self, boosts=(), profile=None, **attrib):
        panel = dict(self.attrib, **attrib)
        return getDamageCoeff("3d", panel, boosts, lvl=133, isSangRou=0,
                              gameEdition=160, targetProfile=profile or self.profile)

    def test_current_main_templates_use_actual_level_and_defense(self):
        source = json.loads((ROOT / "equip/resources/cangshengtf/luoyang_npc_defense.json")
                            .read_text(encoding="utf-8"))
        expected = 1000 * (1 - 6399 / (6399 + 11883.168))
        for template in source["mainTemplates"]:
            for school_type in range(1, 6):
                with self.subTest(template=template, school_type=school_type):
                    self.assertAlmostEqual(self.coeff(profile=source["profiles"][template],
                                                     **{"类型": school_type}), expected)

    def test_target_level_overrides_legacy_default_and_player_level(self):
        for level, factor in ((1, 330), (30, 330), (31, 363), (50, 990), (53, 1089), (54, 1122)):
            with self.subTest(level=level):
                profile = copy.deepcopy(self.profile)
                profile["level"] = level
                expected = 1000 * (1 - 6399 / (6399 + 10.912 * factor))
                self.assertAlmostEqual(self.coeff(profile=profile), expected)

    def test_each_school_uses_its_own_defense(self):
        for school_type, school in enumerate(SCHOOLS, 1):
            with self.subTest(school=school):
                profile = copy.deepcopy(self.profile)
                profile["shieldBase"][school] = 0
                self.assertEqual(self.coeff(profile=profile, **{"类型": school_type}), 1000)
                other = school_type % 5 + 1
                self.assertLess(self.coeff(profile=profile, **{"类型": other}), 1000)

    def test_flat_physical_defense_reduction_is_school_scoped(self):
        boosts = [{"atPhysicsShieldAdditional": -1000}]
        expected = 1000 * (1 - 5399 / (5399 + 11883.168))
        self.assertAlmostEqual(self.coeff(boosts), expected)
        for school_type in (2, 3, 4, 5):
            self.assertEqual(self.coeff(boosts, **{"类型": school_type}),
                             self.coeff(**{"类型": school_type}))

    def test_flat_magic_defense_reduction_applies_to_all_magic(self):
        boosts = [{"atMagicShield": -1000}]
        self.assertEqual(self.coeff(boosts), self.coeff())
        expected = 1000 * (1 - 5399 / (5399 + 11883.168))
        for school_type in (2, 3, 4, 5):
            self.assertAlmostEqual(self.coeff(boosts, **{"类型": school_type}), expected)

    def test_flat_percent_and_ignore_are_applied_in_order(self):
        boosts = [{"atPhysicsShieldAdditional": -1000, "atPhysicsShieldPercent": -256}]
        defense = (6399 - 1000) * .75 * .5
        expected = 1000 * (1 - defense / (defense + 11883.168))
        self.assertAlmostEqual(self.coeff(boosts, **{"无视防御A": 512}), expected)

    def test_ignore_and_defense_reduction_do_not_create_negative_defense(self):
        for ignore in (1024, 2048):
            self.assertEqual(self.coeff(**{"无视防御A": ignore}), 1000)
        self.assertEqual(self.coeff([{"atPhysicsShieldAdditional": -10000}]), 1000)
        self.assertEqual(self.coeff([{"atPhysicsShieldPercent": -2048}]), 1000)

    def test_mitigation_stays_capped_at_75_percent(self):
        profile = copy.deepcopy(self.profile)
        profile["shieldBase"]["Physics"] = 10 ** 9
        self.assertEqual(self.coeff(profile=profile), 250)

    def test_missing_or_invalid_profile_fails_explicitly(self):
        invalid = (None, {}, {"level": 53}, {"level": 53, "shieldBase": None},
                   {"level": 53, "shieldBase": {"Physics": None}},
                   {"level": 53, "shieldBase": {"Physics": -1}},
                   {"level": 53, "shieldBase": {"Physics": float("nan")}},
                   {"level": 0, "shieldBase": {"Physics": 6399}})
        for profile in invalid:
            with self.subTest(profile=profile):
                with self.assertRaises(ValueError):
                    getDamageCoeff("3d", self.attrib, [], gameEdition=160, targetProfile=profile)

    def test_legacy_levels_retain_previous_hardcoded_values(self):
        pairs = ((114, 12528, 23256.6), (123, 26317, 48873.6), (133, 79722, 148058.46))
        for level, defense, denominator in pairs:
            with self.subTest(level=level):
                expected = 1000 * (1 - defense / (defense + denominator))
                actual = getDamageCoeff("3d", self.attrib, [], lvl=level, isSangRou=0)
                self.assertAlmostEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
