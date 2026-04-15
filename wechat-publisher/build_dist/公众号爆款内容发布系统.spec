# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['desktop_client.py'],
    pathex=['C:/Users/v_junshshi/WorkBuddy/Claw/wechat-publisher/build_dist'],
    binaries=[],
    datas=[
        ('web', 'web'), ('modules', 'modules'),
        ('tools', 'tools'), ('templates', 'templates'),
        ('static', 'static'), ('output', 'output'),
        ('data', 'data'), ('config.yaml', '.'),
        ('feishu_bots_config.json', '.'),
    ],
    hiddenimports=[
        'flask', 'jinja2', 'markupsafe', 'werkzeug',
        'click', 'itsdangerous', 'requests',
        'PIL', 'Pillow', 'yaml', 'json5',
        'playwright', 'asyncio', 'threading',
        'subprocess', 'urllib', 'webbrowser', 'ctypes',
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
    name='公众号爆款内容发布系统', debug=False,
    console=True, strip=False, upx=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='公众号爆款内容发布系统')
