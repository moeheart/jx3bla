import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundled_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return PROJECT_ROOT


def get_runtime_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return PROJECT_ROOT


def _join_relative(root, relative_path):
    if isinstance(relative_path, (list, tuple)):
        return os.path.join(root, *relative_path)
    return os.path.join(root, relative_path)


def _resolve_case_insensitive_path(path):
    if os.path.exists(path):
        return path

    norm_path = os.path.normpath(path)
    drive, rest = os.path.splitdrive(norm_path)
    if os.path.isabs(rest):
        current = drive + os.sep if drive else os.sep
        parts = [part for part in rest.strip(os.sep).split(os.sep) if part]
    else:
        current = drive if drive else "."
        parts = [part for part in rest.split(os.sep) if part]

    for part in parts:
        try:
            entries = os.listdir(current)
        except OSError:
            return path

        lower_part = part.lower()
        match = None
        for entry in entries:
            if entry.lower() == lower_part:
                match = entry
                break
        if match is None:
            return path
        current = os.path.join(current, match)

    return current


def get_resource_path(relative_path):
    if os.path.isabs(relative_path):
        return _resolve_case_insensitive_path(relative_path)

    bundled_path = _join_relative(get_bundled_root(), relative_path)
    runtime_path = _join_relative(get_runtime_root(), relative_path)

    if os.path.exists(bundled_path):
        return bundled_path
    if os.path.exists(runtime_path):
        return runtime_path
    bundled_path = _resolve_case_insensitive_path(bundled_path)
    if os.path.exists(bundled_path):
        return bundled_path
    runtime_path = _resolve_case_insensitive_path(runtime_path)
    if os.path.exists(runtime_path):
        return runtime_path
    return bundled_path


def get_writable_path(relative_path):
    if os.path.isabs(relative_path):
        return relative_path
    return _join_relative(get_runtime_root(), relative_path)


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent != "":
        os.makedirs(parent, exist_ok=True)


def get_icon_dir():
    return get_resource_path("icons")


def get_icon_path(icon_id, suffix="png"):
    if suffix:
        filename = "%s.%s" % (icon_id, suffix)
    else:
        filename = str(icon_id)
    return get_resource_path(os.path.join("icons", filename))
