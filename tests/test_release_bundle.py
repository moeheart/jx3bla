"""Reject incomplete or stale standard-release data before replacing the EXE."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from release.ReleaseResources import CANGSHENG_FILES
from release.ValidateRelease import validate_archive, validate_inputs


class ArchiveFixture:
    def __init__(self, files):
        self.files = files
        self.toc = dict.fromkeys(files)

    def extract(self, name):
        return self.files[name]


class ReleaseBundleTest(unittest.TestCase):
    def setUp(self):
        self.files = {name: name.encode("utf-8") for name in CANGSHENG_FILES}
        self.hashes = {name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()}

    def test_windows_paths_match_all_eleven_resources(self):
        archive = ArchiveFixture({name.replace("/", "\\"): data for name, data in self.files.items()})
        self.assertEqual(validate_archive(archive, self.hashes), 11)

    def test_missing_required_resource_is_rejected(self):
        del self.files[CANGSHENG_FILES[-1]]
        with self.assertRaisesRegex(ValueError, "missing="):
            validate_archive(ArchiveFixture(self.files), self.hashes)

    def test_changed_embedded_bytes_are_rejected(self):
        self.files[CANGSHENG_FILES[0]] = b"old snapshot"
        with self.assertRaisesRegex(ValueError, "differs from current source"):
            validate_archive(ArchiveFixture(self.files), self.hashes)

    def test_old_tables_and_development_evidence_are_rejected(self):
        for extra in ("equip/resources/Custom_Armor.tab", "equip/resources/cangshengtf/buff.tab"):
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


if __name__ == "__main__":
    unittest.main()
