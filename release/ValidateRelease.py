"""Check standard release inputs or embedded runtime data without running the EXE."""
import argparse
import ast
import hashlib
from pathlib import Path

from release.ReleaseResources import CANGSHENG_FILES


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def normalized_path(path):
    return path.replace("\\", "/").casefold()


def validate_inputs(root=PROJECT_ROOT):
    """Reject an accidental beta release or an incomplete local data snapshot."""
    root = Path(root)
    edition = None
    for node in ast.parse((root / "Constants.py").read_text(encoding="utf-8-sig")).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EDITION" for t in node.targets):
            edition = ast.literal_eval(node.value)
    if not isinstance(edition, str) or not edition or "beta" in edition.casefold():
        raise ValueError("Standard release requires a non-beta EDITION in Constants.py")
    hashes = {}
    for filename in CANGSHENG_FILES:
        data = (root / filename).read_bytes()
        if not data:
            raise ValueError("Empty runtime resource: " + filename)
        hashes[filename] = hashlib.sha256(data).hexdigest()
    return edition, hashes


def validate_archive(archive, expected_hashes):
    """Compare embedded bytes and reject old-season tables or accidental evidence files."""
    entries = {normalized_path(name): name for name in archive.toc}
    expected = {normalized_path(name): digest for name, digest in expected_hashes.items()}
    packaged_resources = {name for name in entries if name.startswith("equip/resources/")}
    missing = set(expected) - packaged_resources
    extra = packaged_resources - set(expected)
    if missing or extra:
        raise ValueError("Unexpected bundled resources; missing=%s; extra=%s" % (sorted(missing), sorted(extra)))
    for filename, digest in expected.items():
        data = archive.extract(entries[filename])
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Bundled resource differs from current source: " + filename)
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inputs-only", action="store_true")
    mode.add_argument("--exe", type=Path)
    args = parser.parse_args()
    edition, hashes = validate_inputs()
    if args.exe:
        # PyInstaller's archive reader opens the binary as data; it never launches it.
        from PyInstaller.archive.readers import CArchiveReader
        count = validate_archive(CArchiveReader(str(args.exe)), hashes)
        print("Verified %s: %d bundled runtime resources match current SHA256 hashes" % (edition, count))
    else:
        print("Verified %s: %d non-empty runtime inputs" % (edition, len(hashes)))


if __name__ == "__main__":
    main()
