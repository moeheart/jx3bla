"""Import the 10009 core tables only after verifying the extraction receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from release.NameGenerator import build_tables, write_tables


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync(report, resources):
    source_manifest = report / 'source/fresh-authorized-01/manifest.json'
    audit = json.loads((report / 'source/source_independent_review.json').read_text(encoding='utf-8'))
    receipt = json.loads(source_manifest.read_text(encoding='utf-8'))
    assert audit['status'] == 'passed' and not audit['failures']
    assert audit['manifests'][0]['manifest_sha256'] == digest(source_manifest)
    assert receipt['client_version'] == '1.6.0.10009'
    assert receipt['version_stable'] and receipt['protected_unchanged']
    manifest_path = resources / 'source_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    names = manifest['core_update']['files']
    entries = {Path(entry['utf8']['path']).name.casefold(): entry for entry in receipt['entries']}
    verified = {}
    # Validate every source before changing any destination.
    for name in names:
        entry = entries[name.casefold()]
        assert entry['fresh'] and entry['acknowledged']
        for source in (entry, entry['utf8']):
            path = Path(source['path'])
            assert path.stat().st_size == source['size'] and digest(path) == source['sha256'], path
        verified[name] = entry['utf8']
    changed = []
    for name, source in verified.items():
        target = resources / name
        if digest(target) != source['sha256']:
            changed.append(name)
        shutil.copyfile(source['path'], target)
        row = next(row for row in manifest['files'] if row['name'] == name)
        row.update(bytes=target.stat().st_size, mtime_ns=target.stat().st_mtime_ns,
                   sha256=digest(target), client_version='1.6.0.10009', client_mode='zhcn_hd',
                   extraction_date='2026-10-29', source_path=source['path'],
                   source_manifest=str(source_manifest))
    tables = build_tables(resources)
    manifest.update(client_version='1.6.0.10009', client_mode='zhcn_hd',
                    source_root=str(report / 'source/critical_files'),
                    extraction_date='2026-10-29', release_version='8.16.2',
                    generated_tables={key: len(value) for key, value in tables.items()})
    manifest['runtime_status'].update(buff_tables='current_10009_hd; edition_160_retains_9506',
                                      equipment_source='161+:10009;160:verified9506 archive')
    manifest['client_version_scope'] = (
        '14 core tables from formal client 10009; edition 160 buff/equipment tables retain '
        'the 9506 snapshot. Derived kungfu, NPC and parameter provenance is recorded '
        'separately in files and attribute_evidence; this importer does not regenerate them.')
    manifest['core_update'] = dict(source_report=str(report), report_manifest=str(source_manifest),
        report_manifest_sha256=digest(source_manifest), files=names,
        verified_source_files=len(verified), sha256_changed_files=len(changed), changed_files=changed)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_tables(tables, resources.parents[2] / 'replayer/NameCangsheng.py')
    return dict(client_version=receipt['client_version'], changed_files=changed,
                generated_tables=manifest['generated_tables'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--resources', type=Path, default=Path('equip/resources/cangshengtf'))
    args = parser.parse_args()
    print(json.dumps(sync(args.report.resolve(), args.resources.resolve()), ensure_ascii=False))
