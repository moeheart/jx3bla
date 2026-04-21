# -*- mode: python ; coding: utf-8 -*-

import os


icon_datas = []
for root, _dirs, files in os.walk("icons"):
    for file in files:
        src = os.path.join(root, file)
        dest = os.path.dirname(src)
        icon_datas.append((src, dest))


beta_datas = [
    ("equip/resources/Custom_Trinket.tab", "equip/resources"),
    ("equip/resources/Custom_Armor.tab", "equip/resources"),
    ("equip/resources/Custom_Weapon.tab", "equip/resources"),
    ("equip/resources/attrib.tab", "equip/resources"),
    ("equip/resources/enchant.tab", "equip/resources"),
    ("equip/resources/item.txt", "equip/resources"),
    ("equip/resources/other.tab", "equip/resources"),
    ("equip/resources/Set.tab", "equip/resources"),
] + icon_datas


a = Analysis(
    ['MainWindow.py'],
    pathex=[],
    binaries=[],
    datas=beta_datas,
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
