# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    hiddenimports=[
        'rasterio', 
        'rasterio._base', 
        'rasterio._shim', 
        'rasterio.vrt', 
        'rasterio.windows', 
        'rasterio.enums',
        'rasterio.sample',
        'rasterio._features',
        'fiona',
    ],
    binaries=[],
    datas=[
    ('shapes/*.shp', 'shapes'),
    ('shapes/*.dbf', 'shapes'),
    ('shapes/*.shx', 'shapes'),
    ('shapes/NE1_50M_SR_W.tif', 'shapes'), 
    ('assets/images/transparent_purple_plane_v1.png', 'assets/images'),
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\images\plane_purple_12in sh.ico',
)
