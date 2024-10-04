# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.pyw'],
    pathex=[],
    hiddenimports=['pyogrio._geometry'],
    binaries=[],
    datas=[
        ('shapes/*.shp', 'shapes'),
        ('shapes/*.dbf', 'shapes'),
        ('shapes/*.shx', 'shapes'),
        ('assets/images/transparent_purple_plane_v1.png', 'assets/images'),
        ('assets/images/ead_ops_tool_32.ico', 'assets/images'),  
        ('C:/Users/grici/miniconda3/Library/share/gdal', 'gdal'),
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
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set this to False to start without terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/ead_ops_tool_32.ico'
    )
