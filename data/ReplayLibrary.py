"""Discover recorder directories and store completed desktop reports outside game folders."""
import hashlib
import json
import os
import sqlite3
import zlib
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


def signature(config):
    # Source selection, network identity and window preferences do not change a replay.
    options = {k: v for k, v in config.item.items() if k not in ('general', 'user')}
    options['mask'] = config.item['general'].get('mask', 0)
    return 'desktop-2-' + hashlib.sha256(json.dumps(options, sort_keys=True).encode()).hexdigest()


def discover_recorders(installation, datatype):
    from FileLookUp import FileLookUp
    lookup = FileLookUp()
    lookup.jx3path = installation
    root = lookup.getDataFolder()
    if not root:
        return []
    suffix = 'combat_logs' if datatype == 'jcl' else 'fight_stat'
    reserved = {'audio', 'cache', 'config', 'export', 'font', 'temporary', 'userdata', 'logs', 'decode', 'curl'}
    records = []
    for account in Path(root).iterdir():
        folder = account / 'userdata' / suffix
        if not folder.is_dir():
            continue
        try:
            for role in account.iterdir():
                if role.is_dir() and role.name.casefold() not in reserved:
                    records.append((role.stat().st_mtime_ns, role.name, folder))
        except OSError:
            continue
    # Two accounts may contain a role with the same name. Keep both directories.
    return [(name, folder) for _, name, folder in sorted(records, key=lambda r: (-r[0],r[1],r[2]))]


def fingerprint(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def same_raid(first, second):
    if first is None or first.parent != second.parent:
        return False
    a, b = first.name.split('-', 7), second.name.split('-', 7)
    return len(a) == len(b) == 8 and a[:3] == b[:3] and a[6] == b[6]


def list_logs(folder):
    result = {}
    for path in folder.iterdir():
        if path.name.lower().endswith(('.jcl', '.fstt.jx3dat')):
            try:
                if path.is_file():
                    result[path] = fingerprint(path)
            except FileNotFoundError:
                continue
    return dict(sorted(result.items(), key=lambda item: item[0].name, reverse=True))


def log_labels(path, stamp):
    from tools.Names import getJclEncounter
    map_name, boss = getJclEncounter(path.name) if path.suffix.lower() == '.jcl' else ('未知', '未知')
    try:
        # JCL filenames use game time; the catalog displays local time consistently.
        game = datetime.strptime(path.name[:19], '%Y-%m-%d-%H-%M-%S')
        when = game.replace(tzinfo=timezone(timedelta(hours=8))).astimezone()
    except ValueError:
        when = datetime.fromtimestamp(stamp[1] / 1e9)
    return (when.strftime('%Y-%m-%d %H:%M'), path.name if boss == '未知' else boss, map_name)


def header(result):
    return dict(bossAnalyseName=result.bossAnalyseName, mapDetail=result.mapDetail, server=result.server,
                timestamp=result.timestamp, battleTime=result.battleTime, win=result.win, mask=result.mask,
                statDict=[{'name':row['name'],'occ':row.get('occ','0')} for row in result.statDict],
                potList=result.potList,
                links={name:entry['result']['overall']['shortID']
                       for name,entry in getattr(result,'occResult',{}).items()
                       if entry.get('result',{}).get('overall',{}).get('shortID')})


def _packed(value):
    return zlib.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), 3)


def _unpack(data):
    return json.loads(zlib.decompress(data))


class ReplayLibrary:
    def __init__(self, path):
        self.path = Path(path)

    def _connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path, timeout=8)
        db.execute('''CREATE TABLE IF NOT EXISTS replay (
                    path TEXT PRIMARY KEY, folder TEXT, size INTEGER, stamp INTEGER, version TEXT,
                    summary BLOB, result BLOB, equipment BLOB)''')
        db.execute('CREATE INDEX IF NOT EXISTS replay_folder ON replay(folder,version)')
        return db

    def summaries(self, folder, files, version):
        if not self.path.is_file():
            return {}
        output = {}
        with closing(self._connect()) as db:
            for name, size, stamp, data in db.execute(
                'SELECT path,size,stamp,summary FROM replay WHERE folder=? AND version=?',
                    (os.path.normcase(str(folder)),version)):
                path = Path(name)
                if files.get(path) == (size, stamp):
                    try:
                        output[path] = SimpleNamespace(**_unpack(data))
                    except (TypeError, ValueError, zlib.error):
                        continue
        return output

    def save(self, path, stamp, version, result, session):
        payload = vars(result).copy()
        history = payload.get('bh')
        if history is not None and not isinstance(history, dict):
            payload['bh'] = {k:getattr(history,k,None) for k in (
                'startTime','finalTime','log','badPeriodDpsLog','badPeriodHealerLog')}
        equipment = [session.playerEquipment, session.playerEquipmentAnalysed, session.playerEquipmentOwners]
        args = (os.path.normcase(str(path)),os.path.normcase(str(path.parent)),*stamp,version,
                _packed(header(result)),_packed(payload),_packed(equipment))
        with closing(self._connect()) as db, db:
            db.execute('INSERT OR REPLACE INTO replay VALUES (?,?,?,?,?,?,?,?)', args)

    def load(self, path, stamp, version):
        if not self.path.is_file():
            return None
        with closing(self._connect()) as db:
            record = db.execute('SELECT summary,result,equipment FROM replay WHERE path=? AND size=? AND stamp=? AND version=?',
                                (os.path.normcase(str(path)),*stamp,version)).fetchone()
        if record:
            try:
                meta, payload, equipment = map(_unpack, record)
                payload['potList'] = meta['potList']
                for name, short_id in meta.get('links', {}).items():
                    if name in payload.get('occResult', {}):
                        payload['occResult'][name]['result']['overall']['shortID'] = short_id
                if isinstance(payload.get('bh'), dict):
                    payload['bh'] = SimpleNamespace(**payload['bh'])
                equipment[2] = {k:tuple(owner) for k,owner in equipment[2].items()}
                return SimpleNamespace(**payload), equipment
            except (KeyError, ValueError, TypeError, zlib.error):
                return None

    def previous_equipment(self, path, version, after=None):
        if not self.path.is_file() or not same_raid(path, path):
            return None
        with closing(self._connect()) as db:
            rows = db.execute('''SELECT path,size,stamp FROM replay WHERE folder=? AND version=?
                                 AND path<? AND path>? ORDER BY path DESC''',
                              (os.path.normcase(str(path.parent)), version, os.path.normcase(str(path)),
                               os.path.normcase(str(after)) if after else ''))
            for name, size, stamp in rows:
                source = Path(name)
                if source.name[:10] != path.name[:10]:
                    break
                if not same_raid(source, path):
                    continue
                try:
                    if fingerprint(source) == (size, stamp):
                        data = db.execute('SELECT equipment FROM replay WHERE path=?',(name,)).fetchone()
                        equipment = _unpack(data[0])
                        equipment[2] = {k: tuple(owner) for k, owner in equipment[2].items()}
                        return equipment
                except (OSError, ValueError, TypeError, zlib.error):
                    continue
        return None

    def save_notes(self, path, stamp, version, result):
        with closing(self._connect()) as db, db:
            db.execute('UPDATE replay SET summary=? WHERE path=? AND size=? AND stamp=? AND version=?',
                       (_packed(header(result)),os.path.normcase(str(path)),*stamp,version))
