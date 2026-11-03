# -*- mode: python ; coding: utf-8 -*-

import sys

sys.path.insert(0, SPECPATH)
from release.ReleaseResources import EXCLUDED_MODULES, bundle_datas


# The beta entry uses the same formal-server data as the standard client.
beta_datas = bundle_datas(SPECPATH)


a = Analysis(
    ['MainWindow.py'],
    pathex=[],
    binaries=[],
    datas=beta_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=list(EXCLUDED_MODULES),
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MainWindow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['jx3bla.ico'],
)
