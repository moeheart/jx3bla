"""Observed Wujie fixed children use only the native helper's final pools."""
from types import SimpleNamespace
import hashlib
import json
from pathlib import Path
import unittest

from replayer.CombatTracker import BoostCounter, FIXED_EQUIPMENT_DAMAGE, FIXED_EQUIPMENT_WUJIE


class SecondPartyFixedDamageTests(unittest.TestCase):
    def test_explicit_scope_matches_verified_native_sources(self):
        folder = Path(__file__).resolve().parents[1] / 'docs/160/evidence/heroic_equipment20261114'
        proof = json.loads((folder / 'fixed-damage-evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(set(proof['exactLoggedChildren']), FIXED_EQUIPMENT_DAMAGE)
        self.assertEqual(set(proof['addedWujieOccupations'] + proof['previouslyAuditedWujie']), FIXED_EQUIPMENT_WUJIE)
        for source in proof['sources']:
            for field, hashfield in (('rawPath', 'rawSha256'), ('readablePath', 'readableSha256'),
                                    ('disassemblyPath', 'disassemblySha256')):
                if field in source:
                    self.assertEqual(hashlib.sha256((folder / source[field]).read_bytes()).hexdigest(), source[hashfield])

    def counter(self, occ):
        return BoostCounter('owner', occ, 0, 10000,
            baseAttribute={'_raw': {'atPhysicsAttackPowerBase': 1000,
                                   'atLunarAttackPowerBase': 1000,
                                   'atGamePlayDamageFinalCof': 256}},
            targetProfiles={'boss': {'level': 54, 'shieldBase': {school: 6592 for school in
                ('Physics', 'Solar', 'Lunar', 'Neutral', 'Poison')}}})

    def rates(self, counter, skill='"1,37561,1"'):
        # Test actual event-school weighting too: physical and lunar damage
        # must each take the fixed path, regardless of the character's school.
        return counter.getRateForEvent(SimpleNamespace(target='boss', full_id=skill,
            fullResult={'0': '4000', '3': '6000'}), '附魔伤害')

    def test_three_new_wujie_profiles_preserve_final_pools_and_observed_total(self):
        for occ in ('5dw', '7pw', '23w'):
            for skill in ('"1,37561,1"', '"1,37562,1"'):
                with self.subTest(occ=occ, skill=skill):
                    counter = self.counter(occ)
                    counter.addBoost('own', {'atActivityDamageFinalCof': 512}, 'owner', 1, 0)
                    counter.addBoost('ordinary', {'atAllTypeAttackPowerBase': 200,
                        'atAllTypeOvercomeBase': 3000, 'atAllTypeCriticalStrike': 3000,
                        'atStrainRate': 256, 'atAllDamageAddPercent': 256,
                        'atDstNpcDamageCoefficient': 256}, 'ordinary-provider', 1, 0)
                    counter.addTargetBoost('boss', 'vulnerable', {
                        'atPhysicsDamageCoefficient': 256, 'atLunarDamageCoefficient': 256,
                        'atPhysicsShieldAdditional': -1000}, 'ordinary-provider', 1, 0)
                    counter.addBoost('game', {'atGamePlayDamageFinalCof': 256}, 'game-provider', 1, 0)
                    counter.addBoost('activity', {'atActivityDamageFinalCof': 256}, 'activity-provider', 1, 0)
                    rates = self.rates(counter, skill)
                    self.assertEqual(set(rates), {'self', 'game', 'activity'})
                    self.assertAlmostEqual(rates['self']['rate'], 1.875/2.625)
                    self.assertAlmostEqual(sum(r['rate'] for r in rates.values()) * 10000, 10000)
                    self.assertEqual(rates['game']['source'], 'game-provider')
                    counter.removeBoost('game', 1000)
                    counter.removeBoost('activity', 1000)
                    self.assertEqual(self.rates(counter, skill), {'self': {'source': 'owner', 'id': 'self', 'rate': 1.0}})

    def test_neighbor_scheme_level_and_unaudited_profiles_keep_normal_model(self):
        for occ in ('5dw', '7pw', '23w', '4mw', '3dw'):
            counter = self.counter(occ)
            counter.addBoost('ap', {'atAllTypeAttackPowerBase': 200}, 'provider', 1, 0)
            if occ in ('5dw', '7pw', '23w'):
                self.assertNotIn('ap', self.rates(counter))
            else:
                self.assertGreater(self.rates(counter)['ap']['rate'], 0)
            for skill in ('1,37560,1', '1,37563,1', '2,37561,1', '1,37561,2',
                          '1,37562,2', '"1,37561,1', '1,37561,1"'):
                with self.subTest(occ=occ, skill=skill):
                    self.assertGreater(self.rates(counter, skill)['ap']['rate'], 0)


if __name__ == '__main__':
    unittest.main()
