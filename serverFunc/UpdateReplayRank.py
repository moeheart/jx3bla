# Created by moeheart at 06/07/2022
# 更新复盘的数据排行，用于刷新复盘中各项数据的百分位数并存在数据库中。

import numpy as np
import pymysql
import configparser
import json
import time
import math
from itertools import islice
import urllib.request
from tools.Names import *
from tools.Functions import parseEdition
from tools.Rank import percentile_rank, rank_metric_value
from tools.RecordQuality import (get_record_quality, is_metric_rank_eligible,
                                SENSITIVE_METRICS, parse_statistics)

# 数据库的屎山
STAT_ID = {"score": 3, "rhps": 18, "hps": 20, "rdps": 22, "ndps": 24, "mrdps": 26, "mndps": 28}
RANK_ID = {"score": 17, "rhps": 19, "hps": 21, "rdps": 23, "ndps": 25, "mrdps": 27, "mndps": 29}

DEFAULT_MIN_RANK_CLIENT = "8.13.0"
MIN_RANK_CLIENT_BY_GAME_EDITION = {
    "160": "8.16.0",
    "161": "8.16.0",
    "162": "8.16.0",
}


def isReplayRankEligible(record):
    """Keep uncalibrated older clients out of Cangsheng percentile samples."""
    edition = record[10]
    minimum = MIN_RANK_CLIENT_BY_GAME_EDITION.get(str(record[31]), DEFAULT_MIN_RANK_CLIENT)
    if not isinstance(edition, str) or "beta" in edition.lower():
        return False
    try:
        return parseEdition(edition) >= parseEdition(minimum)
    except (ValueError, IndexError):
        return False


def _read_replay(row):
    try:
        with open("database/ReplayProStat/%d" % row[8], encoding="utf-8-sig") as stream:
            return stream.read()
    except (FileNotFoundError, UnicodeError):
        return None


def _sample(record, text):
    """Derive all sample metrics and the SQL rank eligibility from one file image."""
    try:
        d = parse_statistics(text) if text is not None else None
    except (ValueError, SyntaxError):
        d = None
    if d is None:
        return {}, False
    quality = get_record_quality(d)
    key1 = record[2]
    key2 = getIDFromMap(record[5])
    key3 = record[6]
    key6 = record[31]
    if key2 not in MAP_DICT_RECORD_LOGS or MAP_DICT_RECORD_LOGS[key2] == 1 or key3 not in BOSS_RAW:
        return {}, quality["precise"]
    res = {}
    playerIDloaded = d["overall"]["playerID"]
    if "·" in playerIDloaded:
        playerIDloaded = playerIDloaded.split("·")[0]
    if record[1] != playerIDloaded:
        return {}, False

    skillStat = d["skill"]
    for skill_name, skill in skillStat.items():
        for metric, raw_value in skill.items():
            if not is_metric_rank_eligible(quality, metric):
                continue
            value = rank_metric_value(metric, raw_value, skill)
            if value is not None:
                key = "%s-%s-%s-%s-%s-%s" % (key1, key2, key3, skill_name, metric, key6)
                res[key] = value
    if "healer" in d:
        for line in d["healer"]["table"]:
            if line["name"] == record[1]:
                key4 = "healer"
                for key5 in ["heal", "healEff", "rhps", "hps", "ahps", "ohps", "chps"]:
                    if not is_metric_rank_eligible(quality, key5):
                        continue
                    if key5 not in line:
                        continue
                    key = "%s-%s-%s-%s-%s-%s" % (key1, key2, key3, key4, key5, key6)
                    if not isinstance(line[key5], (int, float)) or not math.isfinite(line[key5]):
                        continue
                    res[key] = line[key5]

    for id in STAT_ID:
        if not is_metric_rank_eligible(quality, id):
            continue
        value = record[STAT_ID[id]]
        if id == "score" and value == -1:
            continue
        if value is not None and math.isfinite(value):
            key = "%s-%s-%s-stat-%s-%s" % (key1, key2, key3, id, key6)
            res[key] = value
    return res, quality["precise"]


def getSingleStat(record):
    if not isReplayRankEligible(record):
        return {}
    return _sample(record, _read_replay(record))[0]


def _merge_player_best(best, record, values):
    player = (record[0], record[1])
    for key, value in values.items():
        scores = best.setdefault(key, {})
        if player not in scores or value > scores[player]:
            scores[player] = value


def getAllStat(records):
    """Group a fixed offline set of replay files by metric and player."""
    best = {}
    for record in records:
        _merge_player_best(best, record, getSingleStat(record))
    return {key: list(scores.values()) for key, scores in best.items()}


def getPercent(records):
    return _percentiles(getAllStat(records).items())


def _percentiles(groups):
    percentResults = {}
    percentile_marks = list(range(101))
    for key, scores in groups:
        res_percent = []
        percentile_values = np.percentile(list(scores), percentile_marks)
        for num in percentile_values:
            num = int(num * 100000) / 100000
            if num > 1000000000:
                num = 1000000000
            res_percent.append(num)
        percentResults[key] = {"num": len(scores), "value": str(res_percent)}
    return percentResults


def _collect_snapshot(reader):
    """Take a per-replay committed SQL/file pair; release shared locks after each batch."""
    best = {}
    candidates = []
    cursor = reader.cursor()
    minimum = parseEdition(DEFAULT_MIN_RANK_CLIENT)
    cursor.execute("SELECT hash FROM ReplayProStat WHERE editionFull>=%s ORDER BY hash", (minimum,))
    hashes = cursor.fetchall()
    reader.rollback()
    for start in range(0, len(hashes), 32):
        keys = tuple(item[0] for item in hashes[start:start + 32])
        placeholders = ", ".join(["%s"] * len(keys))
        try:
            # Uploads lock the same primary key FOR UPDATE before replacing the file,
            # and restore it before releasing that lock on a failed transaction.
            cursor.execute("SELECT * FROM ReplayProStat WHERE hash IN (" + placeholders + ") "
                           "AND editionFull>=%s ORDER BY hash LOCK IN SHARE MODE", (*keys, minimum))
            paired = [(row, _read_replay(row)) for row in cursor.fetchall() if isReplayRankEligible(row)]
        finally:
            reader.rollback()  # Read-only transaction. Parsing takes place outside the lock.
        for row, text in paired:
            values, precise = _sample(row, text)
            _merge_player_best(best, row, values)
            if row[30] == 1:
                candidates.append((row, precise))
    return _percentiles((key, scores.values()) for key, scores in best.items()), candidates


def _rank_changes(records, percentiles):
    """Yield changed rows with a snapshot of the inputs used to calculate them."""
    thresholds = {}
    for row, precise in records:
        map_id = getIDFromMap(row[5])
        hold = row[30]
        ranks = {metric: row[index] for metric, index in RANK_ID.items()}
        if map_id == "未知":
            hold = 0
        elif int(map_id) <= 688:
            continue  # Frozen seasons keep their published ranks.
        else:
            for metric, column in STAT_ID.items():
                key = "%s-%s-%s-stat-%s-%s" % (row[2], map_id, row[6], metric, row[31])
                if (metric == "score" and row[column] == -1) or (not precise and metric in SENSITIVE_METRICS):
                    ranks[metric] = -1
                elif key in percentiles and row[column] is not None:
                    if key not in thresholds:
                        thresholds[key] = json.loads(percentiles[key]["value"])
                    ranks[metric] = percentile_rank(row[column], thresholds[key])
        if hold != row[30] or any(ranks[m] != row[i] for m, i in RANK_ID.items()):
            yield (row[7], *(row[column] for column in _RANK_INPUTS.values()), hold, *ranks.values())


# Protect a replay that was re-uploaded while percentile sampling was in progress.
_RANK_INPUTS = {"shortID": 8, "editionfull": 11, "submittime": 15, "gameEdition": 31,
                "hold": 30, **STAT_ID, **{m + "Rank": i for m, i in RANK_ID.items()}}


def updatePercent(percentiles, cursor, candidates):
    """Stage only changed ranks, then apply them in one joined update."""
    outputs = ["hold"] + [m + "Rank" for m in RANK_ID]
    fields = ["hash", *_RANK_INPUTS] + [f"{field} AS new_{field}" for field in outputs]
    cursor.execute("CREATE TEMPORARY TABLE PendingReplayRanks ENGINE=InnoDB AS SELECT "
                   + ", ".join(fields) + " FROM ReplayProStat WHERE 1=0")
    changes = _rank_changes(candidates, percentiles)
    insert = "INSERT INTO PendingReplayRanks VALUES (" + ", ".join(["%s"] * len(fields)) + ")"
    pending = False
    while batch := list(islice(changes, 500)):
        cursor.executemany(insert, batch)
        pending = True
    if pending:
        unchanged = " AND ".join(f"r.{field} <=> p.{field}" for field in _RANK_INPUTS)
        assignments = ", ".join(f"r.{field} = p.new_{field}" for field in outputs)
        cursor.execute("UPDATE ReplayProStat r JOIN PendingReplayRanks p ON r.hash = p.hash "
                       + "SET " + assignments + " WHERE " + unchanged)


def _publish_percentiles(db, connection_options):
    cursor = db.cursor()
    cursor.execute("SELECT GET_LOCK('jx3bla.refresh_replay_rank', 0)")
    if cursor.fetchone()[0] != 1:
        raise RuntimeError("Another replay rank refresh is already running")
    # Bootstrap a new installation before starting the publishing transaction.
    cursor.execute("CREATE TABLE IF NOT EXISTS ReplayProStatRank (name VARCHAR(128), number INT, "
                   "records TEXT) ENGINE=InnoDB DEFAULT CHARSET utf8mb4")
    cursor.execute("SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() "
                   "AND TABLE_NAME IN ('ReplayProStat', 'ReplayProStatRank', 'PreloadInfo')")
    engines = {name.lower(): engine for name, engine in cursor.fetchall()}
    if len(engines) != 3 or any(engine != "InnoDB" for engine in engines.values()):
        raise RuntimeError("Replay rank publication requires transactional InnoDB tables")
    reader = pymysql.connect(**connection_options)
    try:
        percentiles, candidates = _collect_snapshot(reader)
    finally:
        reader.close()
    if not percentiles:
        raise ValueError("No eligible percentile samples; previous publication retained")

    updatePercent(percentiles, cursor, candidates)
    # InnoDB readers keep seeing the last committed snapshot throughout the reload.
    # DELETE participates in this transaction; TRUNCATE or RENAME would commit it.
    cursor.execute("DELETE FROM ReplayProStatRank")
    entries = [(key, data["num"], data["value"]) for key, data in percentiles.items()]
    cursor.executemany("INSERT INTO ReplayProStatRank (name, number, records) VALUES (%s, %s, %s)", entries)
    cursor.execute("SELECT COUNT(*), SUM(OCTET_LENGTH(name) + OCTET_LENGTH(records)) FROM ReplayProStatRank")
    expected_bytes = sum(len(key.encode()) + len(value.encode()) for key, _, value in entries)
    if tuple(cursor.fetchone()) != (len(entries), expected_bytes):
        raise ValueError("Incomplete or truncated replay percentile publication")
    cursor.execute("SELECT datavalue FROM PreloadInfo WHERE datakey = 'rateEdition' FOR UPDATE")
    previous = cursor.fetchone()
    edition = max(int(time.time()), int(previous[0]) + 1 if previous else 0)
    cursor.execute("DELETE FROM PreloadInfo WHERE datakey = 'rateEdition'")
    cursor.execute("INSERT INTO PreloadInfo (datakey, datavalue) VALUES ('rateEdition', %s)", (str(edition),))


def RefreshStat():
    config = configparser.RawConfigParser()
    with open("settings.cfg", encoding="utf-8-sig") as stream:
        config.read_file(stream)
    connection_options = dict(host="127.0.0.1", user=config.get("jx3bla", "username"),
                              password=config.get("jx3bla", "password"), database="jx3bla",
                              port=3306, charset="utf8mb4", autocommit=False)
    db = pymysql.connect(**connection_options)
    try:
        _publish_percentiles(db, connection_options)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()  # Also releases the refresh lock and the connection-local staging table.

    with urllib.request.urlopen("http://localhost:8009/refreshRateData", timeout=30) as response:
        if json.load(response).get("result") != "success":
            raise RuntimeError("Percentiles committed, but API cache refresh failed")


if __name__ == "__main__":
    RefreshStat()
