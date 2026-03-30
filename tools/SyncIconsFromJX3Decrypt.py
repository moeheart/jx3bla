import argparse
import importlib
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "icons"


def parse_ids(raw: str) -> list[int]:
    ids = []
    for part in raw.split(","):
        value = part.strip()
        if not value:
            continue
        ids.append(int(value))
    return sorted(set(ids))


def candidate_roots() -> list[Path]:
    candidates = []

    env_root = os.environ.get("JX3DECRYPT_ROOT", "").strip()
    if env_root:
        candidates.append(Path(env_root))

    candidates.append(Path(r"C:\Develop\26\jx3decrypt"))

    develop_root = Path(PROJECT_ROOT.anchor) / "Develop"
    if develop_root.exists():
        for line in sorted(develop_root.glob("*/jx3decrypt")):
            candidates.append(line)

    result = []
    seen = set()
    for root in candidates:
        key = str(root.resolve()) if root.exists() else str(root)
        if key in seen:
            continue
        seen.add(key)
        result.append(root)
    return result


def resolve_jx3decrypt_root(raw_root: str) -> Path:
    if raw_root:
        root = Path(raw_root)
        if not (root / "critical_files" / "extract_icons.py").exists():
            raise FileNotFoundError("invalid jx3decrypt root: %s" % root)
        return root

    for root in candidate_roots():
        if (root / "critical_files" / "extract_icons.py").exists():
            return root

    raise FileNotFoundError("jx3decrypt root not found")


def load_extract_module(jx3decrypt_root: Path):
    root_text = str(jx3decrypt_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return importlib.import_module("critical_files.extract_icons")


def sync_icons(icon_ids: list[int], jx3decrypt_root: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    module = load_extract_module(jx3decrypt_root)
    return module.extract_icons(icon_ids, output_dir=output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract icon PNGs from a local jx3decrypt checkout into this project's icons directory."
    )
    parser.add_argument("--ids", required=True, help="Comma-separated icon ids, for example 3330,15522,433")
    parser.add_argument("--jx3decrypt-root", default="", help="Optional path to the jx3decrypt repository")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Target directory for PNG icons")
    args = parser.parse_args()

    icon_ids = parse_ids(args.ids)
    if not icon_ids:
        print("[WARN] no icon ids provided")
        return 0

    jx3decrypt_root = resolve_jx3decrypt_root(args.jx3decrypt_root)
    output_dir = Path(args.output_dir)

    print("[INFO] jx3decrypt root:", jx3decrypt_root)
    print("[INFO] output dir:", output_dir)
    print("[INFO] ids:", ",".join(str(line) for line in icon_ids))

    result = sync_icons(icon_ids, jx3decrypt_root, output_dir)

    for icon_id in icon_ids:
        target = output_dir / ("%d.png" % icon_id)
        print("[CHECK] %s -> %s" % (icon_id, "OK" if target.exists() else "MISSING"))

    return result


if __name__ == "__main__":
    raise SystemExit(main())
