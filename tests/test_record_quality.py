"""Quality metadata and bounded cache tests; no database/network involved."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import RecordQuality as quality


class RecordQualityTests(unittest.TestCase):
    def tearDown(self):
        quality.invalidate_quality_cache()

    def test_legacy_and_supported_are_precise(self):
        for data in ({}, {"overall": {"attributeStatus": {"status": "supported"}}}):
            self.assertTrue(quality.get_record_quality(data)["precise"])
            self.assertEqual(quality.quality_level(data), 3)

    def test_estimated_shapes_preserve_measured_metrics(self):
        status = {"status": "estimated", "staticAttributes": "estimated", "estimatedPlayers": {"1": {}},
                  "missingEquipmentPlayers": {"1": {"hasReference": True}}}
        for data in (status, {"overall": {"attributeStatus": status}}, {"statistics": {"attributeStatus": status}},
                     {"act": {"rdpsStatus": status}}):
            with self.subTest(data=data):
                result = quality.get_record_quality(data)
                self.assertFalse(result["precise"])
                self.assertEqual(quality.quality_level(data), 1)
                self.assertEqual(result["estimatedPlayerCount"], 1)
                self.assertEqual(result["missingEquipmentPlayerCount"], 1)
                for metric in ("score", "rdps", "mrdps"):
                    self.assertFalse(quality.is_metric_rank_eligible(data, metric))
                for metric in ("hps", "rhps", "ndps", "mndps", "heal", "healEff", "numPerSec"):
                    self.assertTrue(quality.is_metric_rank_eligible(data, metric))
                self.assertEqual(quality.get_record_quality(result), result)

    def test_static_attributes_and_unmodeled_effects_are_separate(self):
        data = {"status": "supported", "staticAttributes": "available", "unmodeledEffects": ["atSkillEventHandler"]}
        result = quality.get_record_quality(data)
        self.assertEqual(result["staticAttributes"], "available")
        self.assertFalse(result["precise"])
        self.assertEqual(quality.quality_level(data), 2)
        self.assertEqual(result["unmodeledEffects"], ["atSkillEventHandler"])

    def test_missing_reference_is_level_zero(self):
        for state in ("partial", "missing"):
            data = {"status": "incomplete", "staticAttributes": state,
                    "missingEquipmentPlayers": {"2": {"hasReference": False}}}
            self.assertEqual(quality.quality_level(data), 0)
            self.assertFalse(quality.get_record_quality(data)["rankEligible"]["rdps"])

    def test_unsupported_and_invalid_are_not_precise(self):
        for state in ("unsupported", "invalid"):
            self.assertFalse(quality.get_record_quality({"status": state})["precise"])

    def test_negative_missing_and_nan_are_not_valid_ranks(self):
        for value in (-1, None, float("nan"), float("inf"), "90", True):
            self.assertFalse(quality.is_valid_rank(value))
        self.assertTrue(quality.is_valid_rank(0))
        self.assertTrue(quality.is_valid_rank(99))

    def test_parse_preserves_apostrophes_json_and_python_literals(self):
        data = {"overall": {"playerID": "O'Brien", "attributeStatus": {"status": "estimated"}}, "valid": True}
        for text in (json.dumps(data), repr(data)):
            self.assertEqual(quality.parse_statistics(text), data)
        with self.assertRaises((ValueError, SyntaxError)):
            quality.parse_statistics("__import__('os').system('anything')")

    def test_cache_hits_invalidation_file_change_and_missing_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            self.assertEqual(quality.load_record_quality(path)["status"], "unavailable")
            path.write_text('{"overall": {}}', encoding="utf-8")
            real_open = open
            with patch.object(quality, "open", wraps=real_open, create=True) as reader:
                first = quality.load_record_quality(path)
                first["rankEligible"]["score"] = False
                self.assertTrue(quality.load_record_quality(path)["precise"])
                self.assertTrue(quality.load_record_quality(path)["rankEligible"]["score"])
                self.assertEqual(reader.call_count, 1)
                quality.invalidate_quality_cache(path)
                self.assertTrue(quality.load_record_quality(path)["precise"])
                self.assertEqual(reader.call_count, 2)
                path.write_text('{"attributeStatus": {"status": "estimated"}}', encoding="utf-8")
                self.assertFalse(quality.load_record_quality(path)["precise"])
                self.assertEqual(reader.call_count, 3)
            path.write_text("broken", encoding="utf-8")
            self.assertEqual(quality.load_record_quality(path)["status"], "unavailable")
            path.write_text("{}", encoding="utf-8")
            self.assertTrue(quality.load_record_quality(path)["precise"])

    def test_cache_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(quality, "_CACHE_LIMIT", 2):
            for index in range(4):
                path = Path(directory) / str(index)
                path.write_text("{}", encoding="utf-8")
                quality.load_record_quality(path)
            self.assertEqual(len(quality._quality_cache), 2)


if __name__ == "__main__":
    unittest.main()
