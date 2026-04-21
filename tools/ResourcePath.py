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


def get_resource_path(relative_path):
    if os.path.isabs(relative_path):
        return relative_path

    bundled_path = _join_relative(get_bundled_root(), relative_path)
    runtime_path = _join_relative(get_runtime_root(), relative_path)

    if os.path.exists(bundled_path):
        return bundled_path
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
