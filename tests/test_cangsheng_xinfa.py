import hashlib
import json
from pathlib import Path
import unittest

from release.GenerateXinfa50 import skill_level_evidence
from release.GenerateXinfaBuffEvidence import export
from release.Lua51Evidence import Chunk


ROOT = Path(__file__).resolve().parents[1] / 'equip/resources/cangshengtf'
EVIDENCE = ROOT / 'xinfa_evidence'


class XinfaEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'xinfa50.json').read_text(encoding='utf-8'))
        cls.profiles = cls.data['occupations']

    def test_portable_originals_match_manifest_and_bytecode_roundtrip(self):
        manifest = json.loads((EVIDENCE / 'source_manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['files']), 59)
        chunks = 0
        for row in manifest['files']:
            raw = (EVIDENCE / 'unpack_result' / row['origin']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'], row['origin'])
            self.assertEqual(len(raw), row['bytes'])
            if raw.startswith(b'\x1bLua'):
                self.assertEqual(Chunk(raw).serialize(4), raw, row['origin'])
                chunks += 1
        self.assertEqual(chunks, 35)

    def test_all_32_kungfu_levels_are_learned_at_50(self):
        rows = json.loads((EVIDENCE / 'mount_skills.json').read_text(encoding='utf-8'))
        levels = skill_level_evidence(EVIDENCE, rows)
        self.assertEqual(len(levels), 32)
        self.assertEqual(len(self.profiles), 31)
        for profile in list(self.profiles.values()) + list(self.data['alternate_xinfa'].values()):
            self.assertEqual(profile['learning_source'], levels[str(profile['skill_id'])])
            self.assertEqual(profile['skill_level'], 5)

    def test_healer_static_values_and_exact_conversion_denominators(self):
        for occ, therapy, spirit, crit in [('2h', 6367, 686, 82), ('5h', 6822, 727, 41)]:
            profile = self.profiles[occ]
            self.assertEqual(profile['base_attributes']['atTherapyPowerBase'], therapy)
            conversion = {row['target']: row for row in profile['conversions']}
            self.assertEqual(conversion['治疗']['raw'], spirit)
            self.assertEqual(conversion['会心']['raw'], crit)
            self.assertEqual(conversion['治疗']['coefficient'], spirit / 1024)
            self.assertEqual(conversion['会心']['coefficient'], crit / 1024)
        # Two separate MAGIC_SHIELD calls must both survive aggregation.
        self.assertEqual(self.profiles['2h']['base_attributes']['atMagicShield'], 553)

    def test_original_kungfu_has_priority_over_stale_ui_coefficients(self):
        for occ, key, raw in [('21d', 'AGILITY_TO_PARRY_COF', 102),
                              ('21d', 'AGILITY_TO_PARRY_VALUE_COF', 205),
                              ('10t', 'VITALITY_TO_DODGE_COF', 164),
                              ('21t', 'VITALITY_TO_PARRY_COF', 164)]:
            values = {row['enum']: row['raw'] for row in self.profiles[occ]['conversions']}
            self.assertEqual(values[key], raw)

    def test_common_additional_attribute_and_failed_decompiler_are_explicit(self):
        for occ, profile in self.profiles.items():
            value = profile['base_attributes'].get('atDecriticalDamagePowerBaseKiloNumRate', 0)
            self.assertEqual(value, 0 if occ.endswith('t') else 102, occ)
            self.assertEqual(profile['original_bytecode_matches_decompiled'], occ != '10t', occ)
        self.assertIn('L2_2', self.profiles['10t']['decompiler_issue'])
        # The original Mingzun bytecode executes successfully and retains both AP schools.
        names = {row['enum'] for row in self.profiles['10t']['conversions']}
        self.assertIn('VITALITY_TO_SOLAR_ATTACK_POWER_COF', names)
        self.assertIn('VITALITY_TO_LUNAR_ATTACK_POWER_COF', names)

    def test_dynamic_buff_evidence_matches_source_and_does_not_rescale(self):
        data = export(ROOT)
        retained = json.loads((ROOT / 'xinfa_buff_evidence.json').read_text(encoding='utf-8'))
        # The snapshot keeps its original 9503 provenance. Unrelated rows in the
        # refreshed 9506 tables change whole-file hashes; every saved evidence
        # object (including the complete source row and tooltip) must still match.
        self.assertEqual(retained['client_version'], '1.6.0.9503')
        for group in ('conversion_rows', 'critical_effect_rows', 'interpretation'):
            self.assertEqual(data[group], retained[group], group)
        self.assertEqual(len(data['conversion_rows']), 72)
        self.assertEqual(len(data['critical_effect_rows']), 30)
        rows = {(row['buff_id'], row['level']): row for row in data['conversion_rows']}
        def value(identifier, level, attribute):
            return next(float(row['value_a']) for row in rows[(identifier, level)]['effects']
                        if row['attribute'] == attribute)
        self.assertEqual(value(17885, 5, 'atVitalityToPhysicsAttackPowerCof'), 2160)
        self.assertEqual(value(29938, 5, 'atVitalityToPhysicsAttackPowerCof'), 721)
        # The primary/secondary threat versions are distinct integer coefficients,
        # not a base coefficient to multiply mechanically by three again.
        self.assertNotEqual(2160, 721 * 3)


if __name__ == '__main__':
    unittest.main()
