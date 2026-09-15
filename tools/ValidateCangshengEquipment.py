"""Validate actual JCL equipment coverage and the export/import chain, without player names."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from equip.AttributeCal import AttributeCal
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment, ImportExcelEquipment
from tools.LoadData import LuaTableAnalyserToDict


def validate(path):
    raw = path.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('gb18030')
    players = {}
    parser = LuaTableAnalyserToDict()
    for line in text.splitlines():
        fields = line.split('\t')
        if len(fields) > 5 and fields[4] == '4':
            data = parser.analyse(fields[5], delta=1)
            if isinstance(data.get('6'), dict) and data['6']:
                players[data['1']] = {'occ': data['4'], 'equipment': data['6']}
    cal = AttributeCal(160)
    converter, exporter, importer = EquipmentAnalyser(), ExcelExportEquipment(), ImportExcelEquipment()
    stats, values = Counter(), []
    for index, player in enumerate(players.values()):
        converted = converter.convert2(player['equipment'])
        serialized = exporter.export(converted)
        imported = importer.importData(serialized)
        for position, equip in imported.items():
            if equip['id'] in ('', '0'):
                continue
            cal.equipmentInfo.getFeature(equip['id_full'])
            stats['equipment'] += 1
            for slot in range(1, 4):
                key = 'plug%d' % slot
                original = int(converted[position].get(key, 0) or 0)
                assert equip.get(key, 0) == original, (position, key)
                stats['gems'] += bool(original)
        attributes = cal.CalculateAll(serialized)
        values.append({'index': index, 'kungfu': player['occ'], 'attributes': attributes,
                       'warnings': cal.lastWarnings})
    return {'source': path.name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'players': len(players), 'counts': dict(stats), 'results': values}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.log)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('players', 'counts')}, ensure_ascii=False))
