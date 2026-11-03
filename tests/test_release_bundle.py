"""Reject incomplete or stale standard-release data before replacing the EXE."""
import hashlib
from pathlib import Path
import tempfile
import subprocess
import sys
from types import SimpleNamespace
import unittest

from release.ReleaseResources import CANGSHENG_FILES, bundle_datas
from release.ValidateRelease import validate_archive, validate_inputs, validate_dependencies


class ArchiveFixture:
    def __init__(self, files, modules=()):
        self.files = files
        self.toc = dict.fromkeys(files)
        self.modules = modules

    def open_embedded_archive(self, name):
        assert name == "PYZ.pyz"
        return SimpleNamespace(toc=dict.fromkeys(self.modules))

    def extract(self, name):
        return self.files[name]


class ReleaseBundleTest(unittest.TestCase):
    def setUp(self):
        self.files = {name: name.encode("utf-8") for name in CANGSHENG_FILES}
        self.hashes = {name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()}

    def test_windows_paths_match_all_runtime_resources(self):
        archive = ArchiveFixture({name.replace("/", "\\"): data for name, data in self.files.items()})
        self.assertEqual(validate_archive(archive, self.hashes), len(CANGSHENG_FILES))

    def test_missing_required_resource_is_rejected(self):
        del self.files[CANGSHENG_FILES[-1]]
        with self.assertRaisesRegex(ValueError, "missing="):
            validate_archive(ArchiveFixture(self.files), self.hashes)

    def test_changed_embedded_bytes_are_rejected(self):
        self.files[CANGSHENG_FILES[0]] = b"old snapshot"
        with self.assertRaisesRegex(ValueError, "differs from current source"):
            validate_archive(ArchiveFixture(self.files), self.hashes)

    def test_old_tables_and_development_evidence_are_rejected(self):
        for extra in ("equip/resources/Custom_Armor.tab", "equip/resources/cangshengtf/buff.tab",
                      "docs/160/evidence/xinfa/source_manifest.json"):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "extra="):
                validate_archive(ArchiveFixture(dict(self.files, **{extra: b"unexpected"})), self.hashes)

    def test_standard_inputs_reject_beta_and_empty_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            constants = root / "Constants.py"
            constants.write_text('EDITION = "8.16.0-beta.2"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-beta"):
                validate_inputs(root)
            constants.write_text('EDITION = "8.16.0"\n', encoding="utf-8")
            for name, data in self.files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            edition, hashes = validate_inputs(root)
            self.assertEqual((edition, hashes), ("8.16.0", self.hashes))
            (root / CANGSHENG_FILES[-1]).write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "Empty runtime resource"):
                validate_inputs(root)


    def test_current_resources_do_not_collect_old_tables_or_icon_caches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("icons/1.png", "icons/jx3bla.ico", "icons/2.PNG",
                         "icons/rate.dat", "icons/test.py", "icons/__pycache__/test.pyc",
                         "icons/cache/unrelated.png"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            (root / "icons/directory.png").mkdir()
            for name in ("equip/resources/Custom_Armor.tab",
                         "equip/resources/cangshengtf/cangsheng_test_equipment.zip"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"obsolete")
            files = {Path(src).relative_to(root).as_posix() for src, _ in bundle_datas(root)}
            self.assertEqual(files, set(CANGSHENG_FILES))

    def test_optional_native_and_python_dependencies_are_rejected(self):
        for extra in ("numpy\\_core\\_multiarray.pyd", "numpy.libs\\blas.dll",
                      "numpy-2.3.5.dist-info\\METADATA", "PIL\\_avif.cp314-win_amd64.pyd"):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "optional bundled"):
                validate_dependencies(ArchiveFixture({extra: b"unused"}))
        for module in ("numpy", "numpy.linalg", "PIL.AvifImagePlugin", "PIL._avif",
                       "replayer.NameCangsheng", "replayer.NameCangshengTest", "equip.AttributeData"):
            with self.subTest(module=module), self.assertRaisesRegex(ValueError, "optional bundled"):
                validate_dependencies(ArchiveFixture({}, modules=[module]))
        validate_dependencies(ArchiveFixture({"PIL\\_imaging.pyd": b"required"},
                                             modules=["openpyxl", "PIL.PngImagePlugin", "PIL.IcoImagePlugin"]))

    def damage_tracker(self):
        # The attacker is active for 10 s and the credited support for 5 s.
        # Moving 200 raw damage raises total displayed DPS from 100 to 120.
        return SimpleNamespace(
            info=SimpleNamespace(npc={'npc': object()}), boostCounter={'attacker': object(), 'support': object()},
            ndps={'sum': 100, 'player': {'attacker': {'sum': 1000, 'adjustedTime': 10000}}},
            rdps={'sum': 120, 'player': {'attacker': {'sum': 800, 'adjustedTime': 10000},
                                        'support': {'sum': 200, 'adjustedTime': 5000}}},
            ndpsCast={'attacker': SimpleNamespace(sum=1000), 'support': SimpleNamespace(sum=0),
                      'npc': SimpleNamespace(sum=37)},
            rdpsCast={'attacker': SimpleNamespace(sum=800), 'support': SimpleNamespace(sum=200)},
            mndpsCast={'attacker': SimpleNamespace(sum=500), 'support': SimpleNamespace(sum=0)},
            mrdpsCast={'attacker': SimpleNamespace(sum=400), 'support': SimpleNamespace(sum=100)},
        )

    def test_raw_damage_conservation_ignores_different_active_times_and_npc_damage(self):
        from release.SmokeTest import check_damage_conservation
        tracker = self.damage_tracker()
        self.assertNotEqual(tracker.ndps['sum'], tracker.rdps['sum'])
        result = check_damage_conservation(tracker)
        self.assertEqual(result['directDamage'], 1000)
        self.assertEqual(result['redistributedDamage'], 1000)
        self.assertEqual(result['excludedNpcDamage'], 37)
        self.assertEqual(result['conservationError'], 0)
        self.assertEqual(result['mainTargetConservationError'], 0)

    def test_raw_damage_conservation_still_rejects_lost_attributed_damage(self):
        from release.SmokeTest import check_damage_conservation
        for recorder in ('rdpsCast', 'mrdpsCast'):
            tracker = self.damage_tracker()
            getattr(tracker, recorder)['support'].sum -= 1
            with self.subTest(recorder=recorder), self.assertRaises(AssertionError):
                check_damage_conservation(tracker)
        tracker = self.damage_tracker()
        tracker.info.npc = {}
        with self.assertRaises(AssertionError):
            check_damage_conservation(tracker)

    def test_excel_round_trip_without_optional_numpy(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-c",
             "import sys; sys.modules['numpy'] = None; "
             "from release.SmokeTest import check_excel; "
             "assert check_excel() == {'roundTrip': 'passed', 'numpyAvailable': False}"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
