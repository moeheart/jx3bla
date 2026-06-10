# Created by moeheart at 06/10/2026
# Remote server address resolver.

import copy
import json
import urllib.parse
import urllib.request


ADDRESS_SERVICE_URL = "http://jx3blaaddress.moeheart.cn/"
ADDRESS_SERVICE_TIMEOUT = 2

FALLBACK_ADDRESS = {
    "api": {"scheme": "http", "host": "116.211.150.188", "port": 8009},
    "logs": {"scheme": "http", "host": "116.211.150.188", "port": 888},
}

_address_cache = None


def _normalize_target(value, fallback):
    target = copy.deepcopy(fallback)
    if not isinstance(value, dict):
        return target

    scheme = value.get("scheme", target["scheme"])
    host = value.get("host", target["host"])
    port = value.get("port", target.get("port"))

    if isinstance(scheme, str) and scheme:
        target["scheme"] = scheme
    if isinstance(host, str) and host:
        target["host"] = host
    try:
        target["port"] = int(port)
    except (TypeError, ValueError):
        target["port"] = fallback.get("port")
    return target


def _load_remote_address():
    with urllib.request.urlopen(ADDRESS_SERVICE_URL, timeout=ADDRESS_SERVICE_TIMEOUT) as resp:
        data = json.load(resp)
    return {
        "api": _normalize_target(data.get("api"), FALLBACK_ADDRESS["api"]),
        "logs": _normalize_target(data.get("logs"), FALLBACK_ADDRESS["logs"]),
    }


def get_address_config():
    global _address_cache
    if _address_cache is not None:
        return _address_cache
    try:
        _address_cache = _load_remote_address()
    except Exception:
        _address_cache = copy.deepcopy(FALLBACK_ADDRESS)
    return _address_cache


def _build_url(kind, path="", query=None):
    target = get_address_config()[kind]
    scheme = target.get("scheme", "http")
    host = target["host"]
    port = target.get("port")

    netloc = host
    if port is not None:
        netloc = "%s:%s" % (host, port)

    if not path:
        path = "/"
    elif not path.startswith("/"):
        path = "/" + path

    url = "%s://%s%s" % (scheme, netloc, path)
    if query:
        connector = "&" if "?" in url else "?"
        url += connector + urllib.parse.urlencode(query)
    return url


def get_api_url(path="", query=None):
    return _build_url("api", path, query)


def get_logs_url(path="", query=None):
    return _build_url("logs", path, query)
