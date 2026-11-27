"""Read and refresh the desktop percentile cache."""
import json
import os
import tempfile
import urllib.request
from contextlib import suppress

from Constants import EDITION, get_api_url
from tools.Functions import parseEdition
from tools.ResourcePath import ensure_parent_dir, get_resource_path, get_writable_path


def read_rate_cache():
    name = os.path.join("icons", "rate.dat")
    path = get_writable_path(name)
    if not os.path.isfile(path):
        path = get_resource_path(name)
    try:
        with open(path, encoding="utf-8-sig") as stream:
            cached = json.load(stream)
        if isinstance(cached["data"], dict):
            return int(cached["edition"]), cached["data"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return -1, {}


def checkRateEdition(serverEdition):
    return refresh_rate_cache(serverEdition, read_rate_cache())[1]


def refresh_rate_cache(serverEdition, cached):
    edition, data = cached
    if edition >= int(serverEdition) or parseEdition(EDITION) == 0:
        return cached
    with urllib.request.urlopen(get_api_url('/getPercentInfo'), timeout=30) as response:
        update = json.load(response)
    if not isinstance(update.get("data"), dict) or not update["data"]:
        raise ValueError("排名数据格式错误")
    version = update.get("rateEdition", serverEdition)
    if int(version) < int(serverEdition):
        raise ValueError("排名分布版本早于公告")
    path = get_writable_path(os.path.join("icons", "rate.dat"))
    ensure_parent_dir(path)
    fd, temporary = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"edition": version,
                       "data": update["data"]}, stream)
        os.replace(temporary, path)
    finally:
        with suppress(FileNotFoundError):
            os.unlink(temporary)
    return int(version), update["data"]
