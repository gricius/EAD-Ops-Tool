# main.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Manually specify 'mplcursors' as a hidden import
hiddenimports = ['pyogrio._geometry', 'mplcursors']

a = Analysis(
    ['main.pyw'],
    pathex=['C:/Users/grici/repos/EAD OPS Tool'],  # Update with your project path
    hiddenimports=hiddenimports,
    binaries=[],  # No additional binaries for 'mplcursors'
    datas=[
        ('shapes/*.shp', 'shapes'),
        ('shapes/*.dbf', 'shapes'),
        ('shapes/*.shx', 'shapes'),
        ('assets/images/transparent_purple_plane_v1.png', 'assets/images'),
        ('assets/images/ead_ops_tool_16.ico', 'assets/images'),
        ('C:/Users/grici/miniconda3/Library/share/gdal', 'gdal'),
    ],
    hookspath=['./hooks'],  # Ensure this path is correct
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to start without terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/ead_ops_tool_16.ico'
)
