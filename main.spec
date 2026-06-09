# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('DBC', 'DBC'),
        ('progress_bar', 'progress_bar'),
        ('backend', 'backend'),
        ('grp1.png', '.'),
        ('logo_only.png', '.'),
        ('app_back.png', '.'),
        ('left-arrow_2.png', '.'),
        ('euler-motors-logo-hd.png', '.'),
        ('check-mark.png', '.')
    ],
    hiddenimports=[
        'openpyxl.cell._writer',
        'pandas', 
        'matplotlib',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs'
    ],
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
    a.zipfiles,
    a.datas,
    name='PARSER',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    runtime_tmpdir=None,
)