# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_client.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web'), ('modules', 'modules'), ('templates', 'templates'), ('static', 'static'), ('tools', 'tools'), ('output', 'output'), ('config.yaml', '.')],
    hiddenimports=['flask', 'jinja2', 'werkzeug', 'PIL', 'yaml', 'urllib3', 'certifi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'numpy', 'pandas'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='公众号爆款内容发布系统',
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
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='公众号爆款内容发布系统',
)
