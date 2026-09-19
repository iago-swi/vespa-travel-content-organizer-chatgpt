import runpy
from pathlib import Path
runpy.run_path(str(Path(SPECPATH) / 'prepare_build.py'))
release = runpy.run_path(str(Path(SPECPATH) / 'app_info.py'))
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('assets/vespa.ico', 'assets'), ('assets/check.svg', 'assets')]
datas += collect_data_files('tzdata')


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
# Windows 10+ supplies its own API sets and Universal CRT. Do not shadow them
# with legacy compatibility shims found in the build runtime.
a.binaries = [entry for entry in a.binaries if not entry[0].lower().startswith(('api-ms-win-', 'ext-ms-win-')) and entry[0].lower() not in {'ucrtbase.dll', 'icuuc.dll', 'icudt78.dll'}]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=release['APP_NAME'],
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/vespa.ico',
    version='version_info.txt',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=release['APP_NAME'],
)


