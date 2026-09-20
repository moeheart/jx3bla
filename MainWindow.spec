# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

sys.path.insert(0, SPECPATH)
from release.ReleaseResources import CANGSHENG_FILES

# Game edition 160 uses the local calculator in both standard and beta builds.
# Keep the standard bundle limited to its required, versioned runtime snapshot.
runtime_datas = [
    (str(Path(SPECPATH) / filename), str(Path(filename).parent))
    for filename in CANGSHENG_FILES
]

a = Analysis(
    ['MainWindow.py'],
    pathex=[],
    binaries=[],
    datas=runtime_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
