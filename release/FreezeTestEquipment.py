"""Preserve the verified 9506 equipment snapshot for edition-160 log replay."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

FILES = ('Custom_Trinket.tab', 'Custom_Armor.tab', 'Custom_Weapon.tab',
         'attrib.tab', 'enchant.tab', 'item.txt', 'other.tab', 'Set.tab')


def freeze(source, output):
    manifest = json.loads((source / 'source_manifest.json').read_text(encoding='utf-8'))
    records = {row['name']: row for row in manifest['files']}
    contents = {}
    for name in FILES:
        data = (source / name).read_bytes()
        assert records[name]['client_version'] == '1.6.0.9506'
        assert hashlib.sha256(data).hexdigest() == records[name]['sha256'], name
        contents[name] = data
    with ZipFile(output, 'w') as archive:
        for name, data in contents.items():
            entry = ZipInfo(name, date_time=(2026, 9, 20, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, data)
        archive.writestr('source_manifest.json', json.dumps(
            dict(client_version='1.6.0.9506', game_edition=160,
                 files=[records[name] for name in FILES]), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    freeze(args.source, args.output)
