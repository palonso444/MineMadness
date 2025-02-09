# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew

path = 'C:\\Users\\Pol Alonso\\Desktop\\Niebla_v3_windows\\'

# Pyinstaller automatically includes all files and folders of the path directory in the build
# (.json, .kv, .png, .ttf, non-main .py files, etc) and detects all imports (json, re, etc)
# to build, navigate to the game directory an type -> pyinstaller pyinstaller.spec

a = Analysis(
    ['main.py'],     
    pathex=[path],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    exclude_binaries=True,
    name='niebla',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe, Tree(path),
    a.binaries,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Niebla',
)
